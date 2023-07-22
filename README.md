# Interapp Audio Merger

Interapp Audio Merger is a simple application that allows you to merge multiple audio files into a single file by dragging and dropping them into the user interface. The application also supports loading audio files from a text file.

## Features

- Drag and drop audio files
- Load audio files from a text file
- Rearrange audio files in the list
- Export merged audio files to a desired location
- Progress bar to show the merging progress
- Compatible with various audio file formats (`.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.aac`)

## Getting Started

These instructions will help you set up the project and run the application on your local machine.

### Prerequisites
- git -> https://git-scm.com/download/win
- python -> https://www.python.org/downloads/
- Python 3.x
- tkinter
- tkinterdnd2
- ffmpeg

### Installation
0. Download and install ffmpeg
1. Clone the repository:

```bash
git clone https://github.com/username/interapp-audio-merger.git
```
2. Change the working directory:
  
```bash
cd interapp-audio-merger
```
4. run the application:
  ```bash
python main.py
```
### Usage

1. Drag and drop the desired audio files into the application, or click the Load files from txt button to load a text file containing file paths of audio files.
2. Rearrange the audio files in the list as needed.
3. Click the ... button to choose the export location for the merged audio file.
4. Click the Build button to merge the audio files.
5. After the merging process is complete, a popup message will appear, indicating that the build operation has been completed successfully.

