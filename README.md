# Discord Video Compressor

This project provides a simple GUI application to compress videos to meet Discord's 10MB file size limit. It aims to help users easily share videos on Discord without compromising too much on quality.

## Features

- Compresses videos to fit within Discord's 10MB file size limit
- User-friendly graphical interface
- Attempts to maintain the highest possible quality while meeting size requirements
- Offers 360p and 480p compression options when possible

## Requirements

- Python 3.7 or higher
- FFmpeg
- PyQt5
- ffmpeg-python

## Installation

1. Clone this repository:
git clone https://github.com/yourusername/discord-video-compressor.git

2. Install the required Python packages:
pip install PyQt5 ffmpeg-python


3. Download FFmpeg from the [official website](https://ffmpeg.org/download.html) and place the `ffmpeg.exe` (or `ffmpeg` on macOS/Linux) in the same directory as the script.

## Usage

Run the script:
python video_compressor_gui.py

1. Click "Select Input File" to choose the video you want to compress.
2. Click "Select Output Directory" to choose where the compressed video will be saved.
3. Click "Compress Video" to start the compression process.
4. If both 360p and 480p versions are available under 10MB, you'll be prompted to choose which one to keep.

## Notes

- The compression process may take some time depending on the size and length of the input video.
- While the script aims for 10MB, the final size might vary slightly.
- Very long videos may not compress to under 10MB even at the lowest quality settings.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/discord-video-compressor/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)

