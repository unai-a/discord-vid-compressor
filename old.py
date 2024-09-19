import os
import subprocess
import ffmpeg
import shutil

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

def compress_to_target_size(input_file, output_dir, target_size_mb=10):
    os.makedirs(output_dir, exist_ok=True)
    
    # Compress to 360p
    output_360p = os.path.join(output_dir, 'output_360p.mp4')
    compress_video(input_file, output_360p, target_size_mb, (640, 360))
    size_360p = get_file_size_mb(output_360p)
    
    # If 360p version is smaller than 7MB, try 480p
    if size_360p < 7:
        output_480p = os.path.join(output_dir, 'output_480p.mp4')
        compress_video(input_file, output_480p, target_size_mb, (854, 480))
        size_480p = get_file_size_mb(output_480p)
        
        if size_480p <= target_size_mb:
            return output_360p, output_480p, size_360p, size_480p
        else:
            os.remove(output_480p)
            return output_360p, None, size_360p, None
    else:
        return output_360p, None, size_360p, None

def main():
    input_file = input("Enter the path to the input video file: ")
    output_dir = input("Enter the directory for output files: ")
    
    if not os.path.exists(input_file):
        print("Input file does not exist.")
        return
    
    try:
        output_360p, output_480p, size_360p, size_480p = compress_to_target_size(input_file, output_dir)
        
        print(f"360p version size: {size_360p:.2f} MB")
        if output_480p:
            print(f"480p version size: {size_480p:.2f} MB")
            
            choice = input("Enter '1' for 360p or '2' for 480p: ")
            if choice == '1':
                os.remove(output_480p)
                final_output = output_360p
            elif choice == '2':
                os.remove(output_360p)
                final_output = output_480p
            else:
                print("Invalid choice. Keeping 360p version.")
                os.remove(output_480p)
                final_output = output_360p
        else:
            print("Only 360p version is available.")
            final_output = output_360p
        
        print(f"Final compressed video saved as: {final_output}")
        print(f"Final size: {get_file_size_mb(final_output):.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while compressing the video: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
