import os
import yt_dlp
import re

# Function to get video URLs from a YouTube channel
def get_video_urls(channel_url):
    # Define options for yt-dlp to extract video information
    ydl_opts = {
        'quiet': True,  # Suppress unnecessary output
        'extract_flat': True,  # Only extract the URLs, don't download any content
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information from the channel URL
        result = ydl.extract_info(channel_url, download=False)
        
        # Extract video URLs if available
        if 'entries' in result:
            video_urls = [entry['url'] for entry in result['entries']]
            return video_urls
        else:
            print("Failed to extract video URLs.")
            return []

# Function to download subtitles from a list of video URLs
def download_subtitles_for_videos(channel_name, video_urls):
    # Create a folder for the channel if it doesn't exist
    if not os.path.exists(channel_name):
        os.makedirs(channel_name)

    # Define options for yt-dlp to download subtitles
    ydl_opts = {
        'quiet': False,
        'writeautomaticsub': True,  # Download automatic subtitles
        'subtitleslangs': ['en'],  # Only download English subtitles
        'skip_download': True,  # Skip video download, only subtitles
        'writesubtitles': True,  # Ensure subtitles are written
        'subtitlesformat': 'best',  # Prefer the best subtitle format
        'write_srt': True,  # Download subtitles in SRT format as well
        'verbose': True,  # Enable verbose output to debug
        'outtmpl': f'{channel_name}/%(title)s.%(ext)s',  # Save subtitles in the channel folder
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for video_url in video_urls:
            video_title = video_url.split('=')[-1]  # Extract video ID from URL
            subtitle_filename_vtt = f"{video_title}.en.vtt"  # Name of the subtitle file (.vtt)
            subtitle_filename_srt = f"{video_title}.en.srt"  # Name of the subtitle file (.srt)

            # Check if either the .vtt or .srt subtitle file already exists
            subtitle_filepath_vtt = os.path.join(channel_name, subtitle_filename_vtt)
            subtitle_filepath_srt = os.path.join(channel_name, subtitle_filename_srt)

            # Skip downloading if subtitles already exist
            if os.path.exists(subtitle_filepath_vtt) or os.path.exists(subtitle_filepath_srt):
                print(f"Subtitles for {video_title} already downloaded.")
            else:
                print(f"Downloading subtitles for video: {video_title}")
                try:
                    ydl.download([video_url])  # Download subtitles for the video
                except Exception as e:
                    print(f"Failed to download subtitles for {video_url}: {e}")

# Function to search subtitles for a specific term
def search_subtitles(search_term, channel_name):
    # Traverse the folder with the channel name to search for subtitles
    found = False
    for root, dirs, files in os.walk(channel_name):
        for file in files:
            if file.endswith('.en.vtt') or file.endswith('.en.srt'):  # Check for both .vtt and .srt subtitle files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Search for the term (case insensitive)
                        if re.search(search_term, content, re.IGNORECASE):
                            print(f"Term found in subtitle: {file_path}")
                            found = True
                except Exception as e:
                    print(f"Error reading subtitle file {file_path}: {e}")

    if not found:
        print("No subtitles found with the search term.")

# Main script
if __name__ == "__main__":
    # Ask for the YouTube channel URL
    channel_url = input("Enter the YouTube channel URL: ")

    # Extract the channel name from the URL
    channel_name = channel_url.split('/')[-2]  # Extract channel name (e.g., '2cells1pack' from '@2cells1pack/videos')

    # Get the list of video URLs from the channel
    video_urls = get_video_urls(channel_url)

    if video_urls:
        # Download subtitles for all videos in the channel if not already downloaded
        download_subtitles_for_videos(channel_name, video_urls)

        # Ask for the search term
        search_term = input("Enter the search term to search in subtitles: ")

        # Search the downloaded subtitles for the search term
        search_subtitles(search_term, channel_name)
    else:
        print("No videos found or failed to fetch video URLs.")
