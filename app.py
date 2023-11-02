import os
import pytube
import tkinter as tk
from tkinter import ttk
from moviepy.editor import *

# Function to sanitize filenames
def sanitize_filename(filename):
    # Replace spaces and special characters with underscores
    return "".join(c if c.isalnum() else "_" for c in filename)

# Function to display download progress
def show_progress(stream, chunk, remaining_bytes):
    total_size = stream.filesize
    bytes_downloaded = total_size - remaining_bytes
    percent_complete = bytes_downloaded / total_size * 100
    terminal_output.insert(tk.END, f"Downloading: {stream.title} ({percent_complete:.2f}%)\n")
    terminal_output.see(tk.END)  # Scroll to the end of the text widget

# Function to handle single video download button click
def download_single_video():
    video_url = video_url_entry.get()
    resolution = resolution_var_single.get()  # Get selected resolution from the combobox

    try:
        video = pytube.YouTube(video_url)
        video_stream = video.streams.filter(res=resolution, file_extension="mp4").first()
        audio_stream = video.streams.filter(only_audio=True).first()

        if video_stream and audio_stream:
            download_path = "downloads"
            os.makedirs(download_path, exist_ok=True)

            video_filename = sanitize_filename(video.title) + "_video.mp4"
            audio_filename = sanitize_filename(video.title) + "_audio.mp3"

            video_path = os.path.join(download_path, video_filename)
            audio_path = os.path.join(download_path, audio_filename)

            video_stream.download(output_path=download_path, filename=video_filename[:-4])
            audio_stream.download(output_path=download_path, filename=audio_filename[:-4])

            # Merge video and audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(os.path.join(download_path, "output.mp4"))

            # Remove temporary video and audio files
            os.remove(video_path)
            os.remove(audio_path)

            terminal_output.insert(tk.END, f"Downloaded: {video.title} ({resolution})\n")
            terminal_output.see(tk.END)  # Scroll to the end of the text widget
        else:
            terminal_output.insert(tk.END, f"Skipped: {video.title} (Video or Audio stream not available)\n")
            terminal_output.see(tk.END)  # Scroll to the end of the text widget
    except Exception as e:
        terminal_output.insert(tk.END, f"Error downloading video: {str(e)}\n")
        terminal_output.see(tk.END)  # Scroll to the end of the text widget
# Function to handle playlist video download button click
def download_playlist_videos():
    playlist_url = playlist_url_entry.get()
    start_index = int(start_entry.get()) - 1
    end_index = int(end_entry.get())
    resolution = resolution_var_playlist.get()  # Get selected resolution from the combobox
    
    try:
        playlist = pytube.Playlist(playlist_url)
        for index, video in enumerate(playlist.videos[start_index:end_index]):
            if resolution in video.streams.filter(res=resolution, file_extension="mp4").first().resolution:
                download_path = "downloads"
                os.makedirs(download_path, exist_ok=True)
                video.register_on_progress_callback(show_progress)
                video.streams.filter(res=resolution, file_extension="mp4").first().download(output_path=download_path)
                terminal_output.insert(tk.END, f"Downloaded: {video.title} ({resolution})\n")
                terminal_output.see(tk.END)  # Scroll to the end of the text widget
            else:
                terminal_output.insert(tk.END, f"Skipped: {video.title} (Not {resolution})\n")
                terminal_output.see(tk.END)  # Scroll to the end of the text widget
    except Exception as e:
        terminal_output.insert(tk.END, f"Error downloading playlist videos: {str(e)}\n")
        terminal_output.see(tk.END)  # Scroll to the end of the text widget

# Create tkinter window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Create and place widgets in the window for single video download
video_url_label = ttk.Label(root, text="Enter YouTube Video URL:")
video_url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

video_url_entry = ttk.Entry(root, width=50)
video_url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

resolution_label_single = ttk.Label(root, text="Select Resolution for Single Video:")
resolution_label_single.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# Combobox for resolution selection for single video
resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p"]
resolution_var_single = tk.StringVar()
resolution_combobox_single = ttk.Combobox(root, textvariable=resolution_var_single, values=resolutions)
resolution_combobox_single.grid(row=1, column=1, padx=10, pady=10, sticky="w")
resolution_combobox_single.set("720p")  # Default resolution selection for single video

download_single_button = ttk.Button(root, text="Download Single Video", command=download_single_video)
download_single_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="we")

# Create and place widgets in the window for playlist video download
playlist_label = ttk.Label(root, text="Enter YouTube Playlist URL:")
playlist_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

playlist_url_entry = ttk.Entry(root, width=50)
playlist_url_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

start_label = ttk.Label(root, text="Enter Start Index (1-based):")
start_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

start_entry = ttk.Entry(root)
start_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

end_label = ttk.Label(root, text="Enter End Index (1-based):")
end_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

end_entry = ttk.Entry(root)
end_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

resolution_label_playlist = ttk.Label(root, text="Select Resolution for Playlist Videos:")
resolution_label_playlist.grid(row=6, column=0, padx=10, pady=10, sticky="w")

# Combobox for resolution selection for playlist videos
resolution_var_playlist = tk.StringVar()
resolution_combobox_playlist = ttk.Combobox(root, textvariable=resolution_var_playlist, values=resolutions)
resolution_combobox_playlist.grid(row=6, column=1, padx=10, pady=10, sticky="w")
resolution_combobox_playlist.set("720p")  # Default resolution selection for playlist videos
download_playlist_button = ttk.Button(root, text="Download Playlist Videos", command=download_playlist_videos)
download_playlist_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="we")

# Create a Text widget for terminal output
terminal_output = tk.Text(root, height=15, width=80)
terminal_output.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="we")

# Run the tkinter main loop
root.mainloop()