import streamlit as st
import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/path/to/ffmpeg"  # Update this to the correct path

import streamlit as st
import shutil
from moviepy.editor import VideoFileClip
# from spleeter.separator import Separator
from pydub import AudioSegment
import ffmpeg

# Metadata extraction functions
def get_duration(video_path):
    probe = ffmpeg.probe(video_path)
    return float(probe['format']['duration'])

def get_resolution(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    return int(video_stream['width']), int(video_stream['height'])

def get_file_size(video_path):
    probe = ffmpeg.probe(video_path)
    return int(probe['format']['size'])

def get_frame_rate(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    return eval(video_stream['avg_frame_rate'])

def get_bit_rate(video_path):
    probe = ffmpeg.probe(video_path)
    return int(probe['format']['bit_rate'])

def get_aspect_ratio(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    return video_stream.get('display_aspect_ratio', f"{video_stream['width']}:{video_stream['height']}")

def get_codec(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    audio_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
    return video_stream['codec_name'], audio_stream['codec_name']

def get_audio_sample_rate(video_path):
    probe = ffmpeg.probe(video_path)
    audio_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
    return int(audio_stream['sample_rate'])

# Data extraction functions
def extract_audio(video_path, output_audio_path, audio_quality):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path, codec='mp3', bitrate=f'{audio_quality}k')
    return output_audio_path

def extract_frames(video_path, output_folder, frame_rate, quality):
    video = VideoFileClip(video_path)
    frame_paths = []
    for i, frame in enumerate(video.iter_frames(fps=frame_rate)):
        frame_path = f"{output_folder}/frame_{i:04d}.jpg"
        frame.save_frame(frame_path, quality=quality)
        frame_paths.append(frame_path)
    return frame_paths

# def separate_audio(audio_path, output_folder):
#     separator = Separator('spleeter:5stems')
#     separator.separate_to_file(audio_path, output_folder)
#     return output_folder

def get_decibel_levels(audio_path):
    audio = AudioSegment.from_file(audio_path)
    decibels = [segment.dBFS for segment in audio[::1000]]  # Measure dBFS every second
    return decibels

# Aggregating everything
def process_video(video_path, audio_quality=192, frame_quality=95, frame_rate=1):
    # Create directories
    frames_folder = 'frames'
    separated_audio_folder = 'separated_audio'
    if not os.path.exists(frames_folder):
        os.makedirs(frames_folder)
    if not os.path.exists(separated_audio_folder):
        os.makedirs(separated_audio_folder)

    # Extract metadata
    metadata = {
        'duration': get_duration(video_path),
        'resolution': get_resolution(video_path),
        'file_size': get_file_size(video_path),
        'frame_rate': get_frame_rate(video_path),
        'bit_rate': get_bit_rate(video_path),
        'aspect_ratio': get_aspect_ratio(video_path),
        'codec': get_codec(video_path),
        'audio_sample_rate': get_audio_sample_rate(video_path),
    }

    # Extract audio
    audio_path = extract_audio(video_path, 'output.mp3', audio_quality)

    # Extract frames
    frame_paths = extract_frames(video_path, frames_folder, frame_rate, frame_quality)

    # # Separate audio components
    # separated_audio_folder = separate_audio(audio_path, separated_audio_folder)

    # Get decibel levels
    decibel_levels = get_decibel_levels(audio_path)

    # Aggregate data results
    data = {
        'audio_path': audio_path,
        'frames': frame_paths,
        # 'separated_audio_folder': separated_audio_folder,
        'decibel_levels': decibel_levels,
    }

    return {'metadata': metadata, 'data': data}

def main():
    st.title("Video Upload Form")

    # Sidebar form
    with st.sidebar:
        st.header("Upload Your Video")
        video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
        
        st.subheader("Video Details")
        video_title = st.text_input("Video Title")
        
        niche_options = [
            "Technology", "Education", "Entertainment", "Lifestyle", 
            "Fitness", "Cooking", "Travel", "Gaming", "Music", "Other"
        ]
        video_niche = st.multiselect("Niche of Video on Social Media", niche_options)

        video_time = st.number_input("Amount of Time Dedicated to Creating the Video (hours)", min_value=0, max_value=100, step=1)
        video_inspiration = st.text_area("Inspiration for Video")
        
        creators_look_up = st.text_input("Creators You Look Up To")
        creators_similar = st.text_input("Creators Who Make Content Similar to Yours")
        reason_for_video = st.text_area("Reason for Video")
        purpose_of_video = st.text_area("Purpose of Video")

        submit_button = st.button("Submit")

    if submit_button: #and video_file is not None:

        st.sidebar.subheader("Submitted Data")
        st.sidebar.markdown(f"**Video Title:** {video_title}")
        st.sidebar.markdown(f"**Niche:** {', '.join(video_niche)}")
        st.sidebar.markdown(f"**Time Dedicated:** {video_time} hours")
        st.sidebar.markdown(f"**Inspiration:** {video_inspiration}")
        st.sidebar.markdown(f"**Creators You Look Up To:** {creators_look_up}")
        st.sidebar.markdown(f"**Creators Similar to You:** {creators_similar}")
        st.sidebar.markdown(f"**Reason for Video:** {reason_for_video}")
        st.sidebar.markdown(f"**Purpose of Video:** {purpose_of_video}")
        st.sidebar.video(video_file)

        # Save uploaded file to a temporary location
        video_path = video_file.name
        with open(video_path, "wb") as f:
            f.write(video_file.getbuffer())

        # Process the video and display results
        st.write("Processing the video... This may take a while.")
        result = process_video(video_path)

        st.subheader("Metadata")
        st.json(result['metadata'])
        
        st.subheader("Extracted Data")

        st.markdown("**Audio Path**")
        st.write(result['data']['audio_path'])

        st.markdown("**Frames**")
        for frame in result['data']['frames']:
            st.image(frame)

        st.markdown("**Separated Audio Components**")
        for root, dirs, files in os.walk(result['data']['separated_audio_folder']):
            for file in files:
                st.write(os.path.join(root, file))

        st.markdown("**Decibel Levels**")
        st.line_chart(result['data']['decibel_levels'])

if __name__ == "__main__":
    # Cleanup directories at the start of the session
    frames_folder = 'frames'
    separated_audio_folder = 'separated_audio'
    if os.path.exists(frames_folder):
        shutil.rmtree(frames_folder)
    if os.path.exists(separated_audio_folder):
        shutil.rmtree(separated_audio_folder)

    main()
