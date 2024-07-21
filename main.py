
import streamlit as st
from pytubefix import YouTube
import ffmpeg
import io
import tempfile
import os

def download_youtube_video(video_url):
    """Downloads the highest resolution YouTube video available at the given URL.

    Args:
        video_url (str): The URL of the YouTube video to download.

    Returns:
        str: The video title if successful, None otherwise.
        bytes: The downloaded video content as bytes if successful, None otherwise.
    """
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.get_highest_resolution()
        video_buffer = io.BytesIO()
        video_stream.stream_to_buffer(video_buffer)
        video_buffer.seek(0)
        st.write(f'Video downloaded successfully: {yt.title}')
        return yt.title, video_buffer.getvalue()  # Return the video title and bytes
    except Exception as e:
        st.write(f'An error occurred: {e}')
        return None, None  # Return None on error


def resize_video_with_audio(video_bytes, output_video_path, 
                            target_width=720, target_height=560, target_fps=25, 
                            video_codec="mpeg4", audio_codec="aac", audio_bitrate="128k", 
                            video_params={}):
    """Resizes a video while preserving the original audio, using specific codecs.

    Args:
        video_bytes (bytes): The video content in bytes.
        output_video_path (str): Path to save the resized video file.
        target_width (int, optional): Target width in pixels. Defaults to 720.
        target_height (int, optional): Target height in pixels. Defaults to 560.
        target_fps (int, optional): Target frames per second. Defaults to 25.
        video_codec (str, optional): Video codec to use. Defaults to "mpeg4".
        audio_codec (str, optional): Audio codec to use. Defaults to "aac".
        audio_bitrate (str, optional): Audio bitrate. Defaults to "128k".
        video_params (dict, optional): Additional video parameters for ffmpeg.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
            temp_input_file.write(video_bytes)
            temp_input_file.flush()
            input_video_path = temp_input_file.name
        
        input_video = ffmpeg.input(input_video_path)
        audio = input_video.audio

        video = (
            input_video
            .filter('scale', target_width, target_height)
            .filter('fps', fps=target_fps)
        )

        output = ffmpeg.output(video, audio, output_video_path,
                               vcodec=video_codec,
                               acodec=audio_codec,
                               audio_bitrate=audio_bitrate,
                               **video_params)
        ffmpeg.run(output, overwrite_output=True)

        st.write(f"Video resized to {target_width}x{target_height} at {target_fps}fps "
                 f"with audio codec {audio_codec} @ {audio_bitrate} and saved to: "
                 f"{output_video_path}")        
        return True  # Indicate success
        
    except Exception as e:
        st.write(f"An error occurred during video processing: {e}")


# --- Streamlit App ---
st.title("YouTube Video Downloader & Resizer")

# Optional Parameters (with default values)
st.sidebar.header("Optional Video Settings")
target_width = st.sidebar.number_input("Target Width (px)", value=720)
target_height = st.sidebar.number_input("Target Height (px)", value=560)
target_fps = st.sidebar.number_input("Target FPS", value=25)
video_codec = st.sidebar.text_input("Video Codec", value="mpeg4")
audio_codec = st.sidebar.text_input("Audio Codec", value="aac")
audio_bitrate = st.sidebar.text_input("Audio Bitrate", value="128k")

# Get YouTube video link from user
video_url = st.text_input("Enter the YouTube video URL:")


if st.button("Download and Process Video"):
    if video_url:
        # 1. Download the video
        st.write("Downloading video...")
        video_title, video_bytes = download_youtube_video(video_url)  # Get the video title and bytes

        if video_title and video_bytes: 
            st.write("Video downloaded. Processing...")

            # 2. Process the video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
                output_path = temp_output_file.name
            
            _ = resize_video_with_audio(video_bytes, output_path,
                                        target_width, target_height, target_fps,
                                        video_codec, audio_codec, audio_bitrate)

            # 3. Provide download link for processed video
            st.write("Processing complete!")
            with open(output_path, "rb") as f:
                st.download_button("Download Processed Video", f, file_name=f"{video_title}.mp4")  

            # Delete the temporary files
            os.remove(output_path)

        else:
            st.write("Error: Failed to download the video.")
    else:
        st.write("Please enter a YouTube video URL.")
