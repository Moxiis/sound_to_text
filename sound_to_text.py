from gradio_client import Client
from pydub import AudioSegment
import ffmpeg
import shutil
import os

session_name = 'sesja_strahd_11_09'
transcription = ''

# functions
def convert_mp4_to_mp3(input_file, output_file):
    try:
        ffmpeg.input(input_file).output(output_file, format='mp3', audio_bitrate='192k').run()
        print(f"Conversion successful: {output_file}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")

mp4_path = fr'C:\Users\dariu\Videos\{session_name}.mp4'
mp3_path = f"{mp4_path.split('.')[0]}.mp3"
convert_mp4_to_mp3(mp4_path, mp3_path)

# create directory for new, shorter mp3 files if it is not existing
dir_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), session_name)
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

# Load your 3-hour MP3 file
audio = AudioSegment.from_mp3(mp3_path)

# Define the duration for each smaller file (20 minutes)
segment_duration = 20 * 60 * 1000  # 20 minutes in milliseconds

# Split the audio into smaller segments
print(f"Starting segmentation")
for i, start in enumerate(range(0, len(audio), segment_duration)):
    segment = audio[start:start + segment_duration]
    segment.export(f"{dir_name}/{i}_{session_name}.mp3", format="mp3")

print("Audio file has been split into smaller segments.")

# connect with API to transcribe all your files
try:
    client = Client("https://openai-whisper.hf.space/")
    for filename in os.listdir(dir_name):
        print(f'working with {filename} file')
        sound_segment = os.path.join(dir_name, filename)
        result = client.submit(
                        sound_segment,	# str (filepath or URL to file) in 'inputs' Audio component
                        "transcribe",	# str in 'Task' Radio component
                        api_name="/predict"
        )
        result = result.result(timeout=1000000)
        transcription += f' {result}'
except:
    with open(fr"C:\code\sound_to_text\transkrypcja\{session_name}.txt", "w") as file:
        file.write(transcription)

# save results to txt file
with open(fr"C:\code\sound_to_text\transkrypcja\{session_name}.txt", "w") as file:
    file.write(transcription)

shutil.rmtree(f'{dir_name}')
