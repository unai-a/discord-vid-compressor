import sys
import os
import subprocess
import ffmpeg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox

def get_video_info(input_file):
    probe = ffmpeg.probe(input_file)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    return {
        'duration': float(probe['format']['duration']),
        'width': int(video_info['width']),
        'height': int(video_info['height']),
    }

def compress_video(input_file, output_file, target_size_mb=10, resolution=None):
    info = get_video_info(input_file)
    duration = info['duration']
    
    target_total_bitrate = (target_size_mb * 8192) / duration
    target_video_bitrate = int(target_total_bitrate * 0.9)
    target_audio_bitrate = int(target_total_bitrate * 0.1)
    
    cmd = [
        'ffmpeg', '-i', input_file,
        '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
        '-b:v', f'{target_video_bitrate}k', '-maxrate', f'{target_video_bitrate*2}k', '-bufsize', f'{target_video_bitrate*4}k',
        '-c:a', 'aac', '-b:a', f'{target_audio_bitrate}k',
    ]
    
    if resolution:
        cmd.extend(['-vf', f'scale={resolution[0]}:{resolution[1]}'])
    
    cmd.extend(['-y', output_file])
    
    subprocess.run(cmd, check=True)

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

class VideoCompressorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        self.input_label = QLabel('Input file: Not selected')
        layout.addWidget(self.input_label)
        
        self.output_label = QLabel('Output directory: Not selected')
        layout.addWidget(self.output_label)
        
        button_layout = QHBoxLayout()
        self.input_button = QPushButton('Select Input File')
        self.input_button.clicked.connect(self.select_input)
        button_layout.addWidget(self.input_button)
        
        self.output_button = QPushButton('Select Output Directory')
        self.output_button.clicked.connect(self.select_output)
        button_layout.addWidget(self.output_button)
        
        layout.addLayout(button_layout)
        
        self.compress_button = QPushButton('Compress Video')
        self.compress_button.clicked.connect(self.compress_video)
        layout.addWidget(self.compress_button)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.setWindowTitle('Video Compressor')
        self.setGeometry(300, 300, 400, 200)
        
    def select_input(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select Input Video', '', 'Video Files (*.mp4 *.avi *.mov *.mkv)')
        if file_name:
            self.input_file = file_name
            self.input_label.setText(f'Input file: {file_name}')
        
    def select_output(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.output_dir = directory
            self.output_label.setText(f'Output directory: {directory}')
        
    def compress_video(self):
        if not hasattr(self, 'input_file') or not hasattr(self, 'output_dir'):
            QMessageBox.warning(self, 'Warning', 'Please select both input file and output directory.')
            return
        
        try:
            self.progress_bar.setValue(0)
            
            output_360p = os.path.join(self.output_dir, 'output_360p.mp4')
            compress_video(self.input_file, output_360p, 10, (640, 360))
            self.progress_bar.setValue(50)
            
            size_360p = get_file_size_mb(output_360p)
            
            if size_360p < 7:
                output_480p = os.path.join(self.output_dir, 'output_480p.mp4')
                compress_video(self.input_file, output_480p, 10, (854, 480))
                self.progress_bar.setValue(75)
                size_480p = get_file_size_mb(output_480p)
                
                if size_480p <= 10:
                    choice = QMessageBox.question(self, 'Choose Version', 
                                                  f'360p version: {size_360p:.2f}MB\n480p version: {size_480p:.2f}MB\nWhich version do you want to keep?',
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    
                    if choice == QMessageBox.Yes:
                        os.remove(output_480p)
                        final_output = output_360p
                    else:
                        os.remove(output_360p)
                        final_output = output_480p
                else:
                    os.remove(output_480p)
                    final_output = output_360p
            else:
                final_output = output_360p
            
            self.progress_bar.setValue(100)
            QMessageBox.information(self, 'Success', f'Video compressed successfully!\nSaved as: {final_output}\nSize: {get_file_size_mb(final_output):.2f}MB')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoCompressorGUI()
    ex.show()
    sys.exit(app.exec_())