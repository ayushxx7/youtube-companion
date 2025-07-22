import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_yt_metadata():
    videos_url = "https://www.youtube.com/@thevibecoder69/videos"
    videos_fname = "yt_videos_metadata.txt"
    shorts_url = "https://www.youtube.com/@thevibecoder69/shorts"
    shorts_fname = "yt_shorts_metadata.txt"

    # Define the order of fields to write
    fields = ["id", "title", "upload_date", "duration", "description", "webpage_url"]

    def write_metadata(fname, metadata_list):
        with open(fname, "w", encoding="utf-8") as f:
            for meta in metadata_list:
                # For any missing field, write empty string
                vals = [meta.get(field, "").replace("\n", " ").replace("\t", " ") for field in fields]
                f.write("\t".join(vals) + "\n")

    # 1. Fetch videos metadata using flat-playlist (faster)
    print(f"Fetching metadata for videos: {videos_url} ...")
    try:
        # Run yt-dlp flat-playlist with print to get all fields line-by-line
        # yt-dlp prints lines: field1, field2, field3... alternating per video, so we parse manually
        result = subprocess.run(
            [
                "yt-dlp", "--flat-playlist",
                "--print", "id",
                "--print", "title",
                "--print", "upload_date",
                "--print", "duration",
                "--print", "description",
                "--print", "webpage_url",
                videos_url
            ],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        # Every video has 6 lines (id, title, upload_date, duration, description, webpage_url)
        videos_metadata = []
        chunk_size = len(fields)
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # skip incomplete chunks
                break
            meta = dict(zip(fields, chunk))
            videos_metadata.append(meta)

        write_metadata(videos_fname, videos_metadata)
        print(f"Saved video metadata to {videos_fname}")

    except Exception as e:
        print(f"Failed to fetch metadata for videos: {e}")

    # 2. Fetch shorts metadata per video (more expensive)

    print(f"Fetching metadata for shorts: {shorts_url} ...")
    try:
        # First get video IDs using flat playlist (id + title is enough here)
        result = subprocess.run(
            [
                "yt-dlp", "--flat-playlist",
                "--print", "id",
                shorts_url
            ],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        video_ids = lines  # Each line is a video id

        shorts_metadata = fetch_all_metadata(video_ids=video_ids[0:5])

        write_metadata(shorts_fname, shorts_metadata)
        print(f"Saved shorts metadata to {shorts_fname}")

    except Exception as e:
        print(f"Failed to fetch metadata for shorts: {e}")

def fetch_metadata_for_video(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    print(f"Fetching metadata for video {vid} ...")
    try:
        result = subprocess.run(
            ["yt-dlp", "-j", url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)

        return {
            "id": info.get("id", ""),
            "title": info.get("title", ""),
            "upload_date": info.get("upload_date", ""),
            "duration": str(info.get("duration", "")),
            "description": info.get("description", "").replace("\n", " ").replace("\t", " "),
            "webpage_url": info.get("webpage_url", url)
        }
    except Exception as e:
        print(f"Failed to fetch metadata for video {vid}: {e}")
        return None

def fetch_all_metadata(video_ids, max_workers=5):
    shorts_metadata = []
    total = len(video_ids)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_vid = {executor.submit(fetch_metadata_for_video, vid): vid for vid in video_ids}
        for future in as_completed(future_to_vid):
            vid = future_to_vid[future]
            try:
                meta = future.result()
                if meta:
                    shorts_metadata.append(meta)
                    completed += 1
                    print(f"[{completed}/{total}] Finished: {vid}")
            except Exception as e:
                print(f"Error fetching video {vid}: {e}")

    print(f"All tasks completed. {len(shorts_metadata)}/{total} videos fetched successfully.")
    return shorts_metadata

if __name__ == "__main__":
    fetch_yt_metadata()
