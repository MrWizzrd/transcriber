import subprocess
import shlex
from pydub import AudioSegment
from .file_utils import print_progress

def convert_video_to_audio(video_path, audio_path):
    try:
        print_progress(f"Converting video to audio: {os.path.basename(video_path)}")
        command = f"ffmpeg -i {shlex.quote(video_path)} -vn -acodec pcm_s16le -ar 44100 -ac 2 {shlex.quote(audio_path)}"
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        print_progress("Conversion completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to audio: {e.stderr.decode()}")
        raise

def split_audio(audio_path, chunk_length_ms=60000):
    print_progress("Splitting audio into chunks")
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i, chunk in enumerate(audio[::chunk_length_ms]):
        chunk_name = f"{audio_path}_chunk_{i}.wav"
        chunk.export(chunk_name, format="wav")
        chunks.append(chunk_name)
    return chunks