import streamlit as st
import os
from pytubefix import YouTube
import ffmpeg

def download_youtube_video(video_url, output_path='.'):
    """Downloads the highest resolution YouTube video available at the given URL.

    Args:
        video_url (str): The URL of the YouTube video to download.
        output_path (str, optional): The directory to save the downloaded video to. 
                                    Defaults to the current working directory.
    """
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.get_highest_resolution()
        video_stream.download(output_path)
        st.write(f'Video downloaded successfully: {yt.title}')
        return yt.title  # Return the video title
    except Exception as e:
        st.write(f'An error occurred: {e}')
        return None  # Return None on error


def resize_video_with_audio(input_video_path, output_video_path, 
                            target_width=720, target_height=560, target_fps=25, 
                            video_codec="mpeg4", audio_codec="aac", audio_bitrate="128k", 
                            video_params = {}):
    """Resizes a video while preserving the original audio, using specific codecs.

    Args:
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path to save the resized video file.
        target_width (int, optional): Target width in pixels. Defaults to 720.
        target_height (int, optional): Target height in pixels. Defaults to 560.
        target_fps (int, optional): Target frames per second. Defaults to 25.
        video_codec (str, optional): Video codec to use. Defaults to "mpeg4".
        audio_codec (str, optional): Audio codec to use. Defaults to "aac".
        audio_bitrate (str, optional): Audio bitrate. Defaults to "128k".
        video_params (dict, optional): Additional video parameters for ffmpeg.
    """
    #try:
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
    # Run ffmpeg and check for errors
    process_result = ffmpeg.run(output, overwrite_output=True)         

    st.write(f"Video resized to {target_width}x{target_height} at {target_fps}fps "
            f"with audio codec {audio_codec} @ {audio_bitrate} and saved to: "
            f"{output_video_path}")        
    return True  # Indicate success
        
    # except Exception as e:
    #     st.write(f"An error occurred during video processing: {e}")
        

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
        video_title = download_youtube_video(video_url)  # Get the video title

        if video_title: 
            # Find the downloaded video file (you can use video_title directly)
            downloaded_file = next((f for f in os.listdir('.') if f.startswith(video_title)), None)

            if downloaded_file:
                st.write("Video downloaded. Processing...")

                # 2. Process the video
                input_path = downloaded_file
                output_path = f"{os.path.splitext(downloaded_file)[0]}_processed.mp4"
                _ = resize_video_with_audio(input_path, output_path,
                                        target_width, target_height, target_fps,
                                        video_codec, audio_codec, audio_bitrate)

                # 3. Provide download link for processed video
                st.write("Processing complete!")
                with open(output_path, "rb") as f:
                    st.download_button("Download Processed Video", f, file_name=downloaded_file)  

                # Delete the downloaded files
                os.remove(downloaded_file)
                os.remove(output_path)

            else:
                st.write("Error: Downloaded video file not found.") 
    else:
        st.write("Please enter a YouTube video URL.")
