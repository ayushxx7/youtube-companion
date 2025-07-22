# by checking whether video is already uploaded to youtube channel -- @thevibecoder69 
# we determine if a file can be deleted. 
# show that on the UI after scan (can delete? Y/N)

import os
import re
from pathlib import Path
import subprocess
from fetch_yt_infoa_via_yt_dlp import fetch_yt_metadata

def parse_yt_metadata(metadata_file: str) -> list[dict]:
    """Parse yt-dlp tab-separated metadata file into a list of dicts."""
    videos = []
    fields = ['id', 'title', 'upload_date', 'duration', 'description', 'url']

    with open(metadata_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            # Fill missing fields with empty strings
            while len(parts) < len(fields):
                parts.append("")

            video = dict(zip(fields, parts[:len(fields)]))
            videos.append(video)
    return videos

def get_local_videos(temp_dir: str) -> list[dict]:
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

