import os
import streamlit as st
import subprocess
import numpy as np
import ffmpeg

class VideoDataExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.probe = ffmpeg.probe(file_path)
        self.video_info = next(stream for stream in self.probe['streams'] if stream['codec_type'] == 'video')
        self.audio_info = next(stream for stream in self.probe['streams'] if stream['codec_type'] == 'audio')

    def get_duration(self):
        return self.probe['format']['duration']

    def get_file_size(self):
        return self.probe['format']['size']

    def get_resolution(self):
        return (self.video_info['width'], self.video_info['height'])

    def get_frame_rate(self):
        return eval(self.video_info['r_frame_rate'])

    def get_video_bit_rate(self):
        return self.video_info['bit_rate']

    # def get_aspect_ratio(self):
    #     return self.video_info['display_aspect_ratio']

    def get_video_codec(self):
        return self.video_info['codec_name']

    def get_audio_bit_rate(self):
        return self.audio_info['bit_rate']

    def get_audio_sample_rate(self):
        return self.audio_info['sample_rate']

    def get_audio_sample_bit_depth(self):
        return self.audio_info['bits_per_sample']

    # def get_decibel_levels(self, chunk_size=1000):
    #     command = [
    #         'ffmpeg', '-i', self.file_path,
    #         '-af', 'volumedetect',
    #         '-f', 'null', '-'
    #     ]

    #     result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    #     output = result.stderr

    #     decibel_levels = []
    #     for line in output.split('\n'):
    #         if 'mean_volume' in line:
    #             parts = line.split()
    #             for part in parts:
    #                 if 'mean_volume:' in part:
    #                     decibel_levels.append(float(part.split(':')[-1].replace('dB', '')))

    #     return decibel_levels

def main():
    st.title("Video Upload Form")

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

    if submit_button and video_file is not None:
        st.sidebar.subheader("Submitted Data")
        st.sidebar.markdown(f"**Video Title:** {video_title}")
        st.sidebar.markdown(f"**Niche:** {', '.join(video_niche)}")
        st.sidebar.markdown(f"**Time Dedicated:** {video_time} hours")
        st.sidebar.markdown(f"**Inspiration:** {video_inspiration}")
        st.sidebar.markdown(f"**Creators You Look Up To:** {creators_look_up}")
        st.sidebar.markdown(f"**Creators Similar to You:** {creators_similar}")
        st.sidebar.markdown(f"**Reason for Video:** {reason_for_video}")
        st.sidebar.markdown(f"**Purpose of Video:** {purpose_of_video}")

        # Save the uploaded file to a temporary location
        temp_video_path = os.path.join("temp_uploaded_video.mov")
        with open(temp_video_path, "wb") as f:
            f.write(video_file.getbuffer())

        # Usage
        extractor = VideoDataExtractor(temp_video_path)

        # Meta information
        duration = extractor.get_duration()
        file_size = extractor.get_file_size()

        # Video information
        resolution = extractor.get_resolution()
        frame_rate = extractor.get_frame_rate()
        video_bit_rate = extractor.get_video_bit_rate()
        # aspect_ratio = extractor.get_aspect_ratio()
        video_codec = extractor.get_video_codec()

        # Audio information
        audio_bit_rate = extractor.get_audio_bit_rate()
        audio_sample_rate = extractor.get_audio_sample_rate()
        audio_sample_bit_depth = extractor.get_audio_sample_bit_depth()

        # Decibel levels
        # decibel_levels = extractor.get_decibel_levels(chunk_size=1000)  # Chunk size in milliseconds
    
        # Display extracted information
        st.markdown("### Extracted Video Data")
        st.markdown(f"**Duration:** {duration} seconds")
        st.markdown(f"**File Size:** {file_size} bytes")
        st.markdown(f"**Resolution:** {resolution[0]}x{resolution[1]}")
        st.markdown(f"**Frame Rate:** {frame_rate} fps")
        st.markdown(f"**Video Bit Rate:** {video_bit_rate} bps")
        # st.markdown(f"**Aspect Ratio:** {aspect_ratio}")
        st.markdown(f"**Video Codec:** {video_codec}")
        st.markdown(f"**Audio Bit Rate:** {audio_bit_rate} bps")
        st.markdown(f"**Audio Sample Rate:** {audio_sample_rate} Hz")
        st.markdown(f"**Audio Sample Bit Depth:** {audio_sample_bit_depth} bits")
        # st.markdown(f"**Decibel Levels:** {decibel_levels}")

        # Clean up temporary file
        os.remove(temp_video_path)

if __name__ == "__main__":
    main()
