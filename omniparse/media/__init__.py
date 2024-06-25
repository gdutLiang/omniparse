            
import os
import tempfile
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from moviepy.editor import VideoFileClip
from omniparse.media.utils import WHISPER_DEFAULT_SETTINGS
from omniparse.media.utils import transcribe  # Assuming transcribe function is imported

def parse_audio(input_data , model_state) -> dict:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(input_data)
                temp_audio_path = temp_audio_file.name
        elif isinstance(input_data, str) and os.path.isfile(input_data):
            temp_audio_path = input_data
        else:
            raise ValueError("Invalid input data format. Expected audio bytes or audio file path.")

        # Transcribe the audio file
        transcript = transcribe(audio_path=temp_audio_path, whisper_model= model_state.whisper_model ,**WHISPER_DEFAULT_SETTINGS)

        return {"message": "Audio parsed successfully", "markdown": transcript['text']}

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

def parse_video(input_data , model_state) -> dict:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
                temp_video_file.write(input_data)
                video_path = temp_video_file.name
        elif isinstance(input_data, str) and os.path.isfile(input_data):
            video_path = input_data
        else:
            raise ValueError("Invalid input data format. Expected video bytes or video file path.")

        # Extract audio from the video
        audio_path = f"{tempfile.gettempdir()}/{os.path.splitext(os.path.basename(video_path))[0]}.mp3"
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()
        video_clip.close()

        # Transcribe the audio file
        transcript = transcribe(audio_path=audio_path, whisper_model= model_state.whisper_model ,**WHISPER_DEFAULT_SETTINGS)

        return {"message": "Audio extracted and parsed successfully", "markdown": transcript['text']}

    finally:
        # Clean up the temporary files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

