import streamlit as st
import deepspeech
import numpy as np
from pydub import AudioSegment

# Initialize DeepSpeech model
MODEL_PATH = "deepspeech-0.9.3-models.pbmm"
model = deepspeech.Model(MODEL_PATH)

def transcribe_audio(audio_data):
    # Perform speech-to-text transcription
    text = model.stt(audio_data)

    return text

def extract_audio(video_file):
    # Extract audio from video
    video_path = "temp_video.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    audio = AudioSegment.from_file(video_path)

    # Convert audio to numpy array
    audio_data = np.array(audio.get_array_of_samples())

    return audio_data

def main():
    st.title("Video Transcript Extractor")

    # Upload video file
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

    if uploaded_file is not None:
        # Extract audio from video
        audio_data = extract_audio(uploaded_file)

        # Transcribe audio
        transcript = transcribe_audio(audio_data)

        # Display transcript
        st.subheader("Transcript:")
        st.write(transcript)

if __name__ == "__main__":
    main()
