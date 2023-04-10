from pydub import AudioSegment
from tqdm import tqdm
from tinytag import TinyTag


def combine_audio_files(audio_files, export_file="combined_audio.mp3",progress_callback=None):
    # Load the first and last audio files
    first_audio = AudioSegment.from_file(audio_files[0])
    last_audio = AudioSegment.from_file(audio_files[-1])

    # Calculate the maximum length of the middle audio files
    max_length = 0

    for audio_file in tqdm(audio_files[1:-1], desc="Calculating max length", unit="file"):
        tag = TinyTag.get(audio_file)
        current_duration = tag.duration * 1000  # Convert to milliseconds
        if current_duration > max_length:
            max_length = current_duration


    # Create a silent audio segment with the maximum length
    middle_audio = AudioSegment.silent(duration=max_length)
    index = 1
    # Overlay all middle audio files onto the silent audio segment
    for audio_file in tqdm(audio_files[1:-1], desc="Combining audio files", unit="file"):
        current_audio = AudioSegment.from_file(audio_file)
        middle_audio = middle_audio.overlay(current_audio)

        if progress_callback:
            progress_callback(index)
            index += 1

    # Combine the first, middle, and last audio files
    combined_audio = first_audio + middle_audio + last_audio

    print("Saving")
    # Export the combined audio to a new file with a lower bitrate
    combined_audio.export(export_file, format="mp3", bitrate="64k")
    print("Saved")

def read_audio_files_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f]


#if __name__ == "__main__":
#    txt_file_path = "backup.txt"  # Replace this with the path to your text file containing audio file paths
#    audio_files = read_audio_files_from_txt(txt_file_path)
#
#    if len(audio_files) < 3:
#        print("At least three audio files are required.")
#    else:
#        combine_audio_files(audio_files)
