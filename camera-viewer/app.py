from flask import Flask, render_template, request, send_from_directory
import subprocess
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# File handler for logging to 'app.log'
file_handler = RotatingFileHandler('app.log', maxBytes=2*1024*1024, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Console handler for debug output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Add handlers if not already present
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
else:
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

CAMERA_DIR = "/sdcard/DCIM/Camera/"
THUMB_DIR = Path("static/thumbnails")
TEMP_DIR = Path("temp")
DOWNLOAD_DIR = Path("downloads")

for p in [THUMB_DIR, TEMP_DIR, DOWNLOAD_DIR]:
    p.mkdir(parents=True, exist_ok=True)

def adb_shell(cmd):
    logger.info(f"Running ADB shell command: {cmd}")
    try:
        result = subprocess.check_output(["adb", "shell"] + cmd.split(), text=True)
        logger.debug(f"ADB output: {result}")
        return result
    except Exception as e:
        logger.error(f"ADB command failed: {cmd} | Error: {e}")
        raise

def parse_ls_date(date_str, time_str):
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return dt
    except Exception as e:
        logger.warning(f"Failed to parse date from ls: {date_str} {time_str} | Error: {e}")
        return None

def list_videos_filtered(start_date, end_date):
    logger.info(f"Listing videos between {start_date} and {end_date}")
    output = adb_shell(f"ls -l {CAMERA_DIR}")
    videos = []
    for line in output.strip().split("\n"):
        parts = line.split()
        if len(parts) < 8: continue  # Adjusted for correct field count
        filename = parts[-1]
        if not filename.lower().endswith(".mp4"): continue
        size = int(parts[4])
        dt = parse_ls_date(parts[5], parts[6])
        if not dt or dt < start_date or dt > end_date:
            continue
        logger.debug(f"Found video: {filename} | Date: {dt}")
        videos.append({
            "name": filename,
            "remote_path": CAMERA_DIR + filename,
            "size_mb": round(size / (1024 * 1024), 1),
            "date": dt.strftime("%Y-%m-%d %H:%M"),
            "expected_size": size
        })
    logger.info(f"Total videos found: {len(videos)}")
    return sorted(videos, key=lambda x: x["date"], reverse=True)

def generate_thumbnail(remote_path, filename, expected_size=None):
    local_full = TEMP_DIR / filename
    thumb_path = THUMB_DIR / (filename + ".jpg")
    placeholder = str(THUMB_DIR / "placeholder.jpg")

    def file_size_ok():
        return expected_size is None or (local_full.exists() and local_full.stat().st_size == expected_size)

    # Try to pull the file if it doesn't exist or size is wrong
    if not file_size_ok():
        logger.info(f"Pulling video from device: {remote_path} -> {local_full}")
        subprocess.run(["adb", "pull", remote_path, str(local_full)], stdout=subprocess.DEVNULL)
        # Check again after pull
        if not file_size_ok():
            logger.error(f"File size mismatch after adb pull: {local_full} (expected {expected_size}, got {local_full.stat().st_size if local_full.exists() else 'missing'})")
            return placeholder, "?:??"

    try:
        logger.info(f"Generating thumbnail for {local_full}")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(local_full),
            "-ss", "00:00:01", "-frames:v", "1", str(thumb_path)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Thumbnail generation failed for {local_full}: {e}")
        return placeholder, "?:??"

    try:
        result = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(local_full)
        ], text=True)
        seconds = float(result.strip())
        duration = f"{int(seconds // 60)}:{int(seconds % 60):02}"
    except Exception as e:
        logger.warning(f"Failed to get duration for {local_full}: {e}")
        duration = "?:??"

    if not thumb_path.exists():
        logger.warning(f"Thumbnail not found for {filename}, using placeholder.")
        return placeholder, duration

    return str(thumb_path), duration

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info(f"Received {request.method} request at /")
    videos = []
    start_date = (datetime.today().replace(hour=0, minute=0) - timedelta(days=2))
    end_date = datetime.today()

    if request.method == "POST":
        try:
            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")
            logger.info(f"User selected date range: {start_date} to {end_date}")
        except Exception as e:
            logger.warning(f"Failed to parse dates from form: {e}")

        video_entries = list_videos_filtered(start_date, end_date)
        for v in video_entries:
            thumb, duration = generate_thumbnail(v["remote_path"], v["name"], v["expected_size"])
            v["thumbnail"] = thumb
            v["duration"] = duration
            videos.append(v)

    return render_template("index.html", videos=videos,
                           default_start=start_date.strftime("%Y-%m-%d"),
                           default_end=end_date.strftime("%Y-%m-%d"))

@app.route("/download/<filename>")
def download_file(filename):
    path = DOWNLOAD_DIR / filename
    temp_path = TEMP_DIR / filename
    if not path.exists():
        if temp_path.exists():
            logger.info(f"Copying file from temp to downloads: {filename}")
            with open(temp_path, "rb") as src, open(path, "wb") as dst:
                dst.write(src.read())
        else:
            logger.info(f"Downloading file from device: {filename}")
            subprocess.run(["adb", "pull", CAMERA_DIR + filename, str(path)])
    else:
        logger.info(f"Serving cached file: {filename}")
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    from datetime import timedelta
    app.run(debug=True, port=5000)
