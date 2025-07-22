# by checking whether video is already uploaded to youtube channel -- @thevibecoder69 
# we determine if a file can be deleted. 
# show that on the UI after scan (can delete? Y/N)

import os
import re
from pathlib import Path
from typing import List, Dict
import subprocess

def parse_yt_metadata(metadata_file: str) -> List[Dict]:
    """Parse yt-dlp metadata file into a list of dicts."""
    videos = []
    with open(metadata_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    # Each video is 6 lines: id, title, upload_date, duration, description, url
    for i in range(0, len(lines), 6):
        if i+5 >= len(lines):
            break
        video = {
            'id': lines[i],
            'title': lines[i+1],
            'upload_date': lines[i+2],
            'duration': lines[i+3],
            'description': lines[i+4],
            'url': lines[i+5],
        }
        videos.append(video)
    return videos

def get_local_videos(temp_dir: str) -> List[Dict]:
    """Get list of local video files and their durations (in seconds)."""
    files = []
    for fname in os.listdir(temp_dir):
        if not fname.lower().endswith('.mp4'):
            continue
        fpath = os.path.join(temp_dir, fname)
        # Get duration using ffprobe
        try:
            result = subprocess.check_output([
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', fpath
            ], text=True)
            duration = float(result.strip())
        except Exception:
            duration = None
        files.append({'filename': fname, 'duration': duration, 'path': fpath})
    return files

def match_video(local, yt_videos, duration_tol=0.5):
    """Return True if local video matches any YouTube video by duration (within tolerance)."""
    matches = []
    if local['duration'] is not None:
        for yt in yt_videos:
            try:
                yt_dur = int(float(yt['duration']))
            except Exception:
                continue
            if abs(local['duration'] - yt_dur) <= duration_tol:
                matches.append(f"{yt['url']} (uploaded {yt['upload_date']})")
    if matches:
        return True, f"Matched by duration: {', '.join(matches)}"
    return False, "No duration match in YouTube uploads"

def fetch_yt_metadata():
    commands = [
        ("yt_videos_metadata.txt", "https://www.youtube.com/@thevibecoder69/videos", True),
        ("yt_shorts_metadata.txt", "https://www.youtube.com/@thevibecoder69/shorts", True),
    ]
    for fname, url, is_flat in commands:
        if not os.path.exists(fname):
            print(f"Fetching metadata for {url} ...")
            try:
                if is_flat:
                    subprocess.run([
                        "yt-dlp", "--flat-playlist",
                        "--print", "id", "--print", "title", "--print", "upload_date", "--print", "duration", "--print", "description", "--print", "webpage_url", url
                    ], check=True, stdout=open(fname, "w", encoding="utf-8"))
                else:
                    subprocess.run([
                        "yt-dlp",
                        "--print", "%(_id)s\n%(_title)s\n%(_upload_date)s\n%(_duration)s\n%(_description)s\n%(_webpage_url)s",
                        url
                    ], check=True, stdout=open(fname, "w", encoding="utf-8"))
                print(f"Saved to {fname}")
            except Exception as e:
                print(f"Failed to fetch metadata for {url}: {e}")

def load_yt_videos():
    metadata_files = ['yt_videos_metadata.txt', 'yt_shorts_metadata.txt']
    yt_videos = []
    for mf in metadata_files:
        if os.path.exists(mf):
            yt_videos.extend(parse_yt_metadata(mf))
    return yt_videos

def main():
    temp_dir = 'temp'
    fetch_yt_metadata()
    metadata_files = ['yt_videos_metadata.txt', 'yt_shorts_metadata.txt']
    yt_videos = []
    found = False
    for mf in metadata_files:
        if os.path.exists(mf):
            found = True
            yt_videos.extend(parse_yt_metadata(mf))
    if not found:
        print(f"You must run yt-dlp to fetch metadata for videos and/or shorts first! See README.")
        return
    local_videos = get_local_videos(temp_dir)
    print(f"{'Filename':40} | Can Delete | Reason")
    print("-"*80)
    for vid in local_videos:
        uploaded, reason = match_video(vid, yt_videos)
        print(f"{vid['filename']:40} | {'Y' if uploaded else 'N'}         | {reason}")

if __name__ == "__main__":
    main()

