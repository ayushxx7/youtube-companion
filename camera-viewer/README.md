# Camera Viewer

A web-based tool to browse, filter, preview, and download videos from your Android device's camera roll using ADB.

## Features
- Browse videos stored in your Android device's camera folder (`/sdcard/DCIM/Camera/`).
- Filter videos by date range using a simple web UI.
- Preview video thumbnails and durations (auto-generated with ffmpeg).
- Download full video files to your computer.
- Robust error handling and logging (to both console and `app.log`).
- Ensures only complete video files are used for preview/thumbnail generation.

## Requirements
- Python 3.7+
- [Flask](https://flask.palletsprojects.com/) (see `requirements.txt`)
- [ADB (Android Debug Bridge)](https://developer.android.com/tools/adb) (must be in your PATH)
- [ffmpeg](https://ffmpeg.org/) and [ffprobe](https://ffmpeg.org/ffprobe.html) (must be in your PATH)
- Your Android device must be connected via USB with USB debugging enabled

## Installation
1. **Clone this repository**
   ```sh
   git clone <repo-url>
   cd camera-viewer
   ```
2. **(Recommended) Create a virtual environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Ensure ADB, ffmpeg, and ffprobe are installed and available in your PATH**
   - On macOS: `brew install android-platform-tools ffmpeg`
   - On Linux: use your package manager

## Usage
1. **Connect your Android device via USB and enable USB debugging.**
2. **Start the Flask app:**
   ```sh
   python3 app.py
   ```
3. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000/
   ```
4. **Filter videos by date, preview thumbnails, and download videos as needed.**

## Running with uv (Optional, Faster Python Startup)
[uv](https://github.com/astral-sh/uv) is a fast Python package manager and runner. You can use it to run this app with even faster startup times.

### Install uv
```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```

### Install dependencies with uv
```sh
uv add -r requirements.txt
```

### Run the app with uv
```sh
uv run app.py
```

The rest of the app usage is the same as above.

## How it works
- The app uses ADB to list and pull video files from your device.
- Thumbnails and durations are generated using ffmpeg/ffprobe.
- Only complete files (matching the size reported by the device) are used for previews.
- All actions are logged to `app.log` and the console for troubleshooting.

## Troubleshooting
- **No videos found:**
  - Make sure your device is connected and authorized for ADB.
  - Ensure there are `.mp4` files in `/sdcard/DCIM/Camera/`.
- **Thumbnails not generated / duration shows `?:??`:**
  - The file may be incomplete or corrupted. Try reloading or reconnecting your device.
- **Download not working:**
  - Check ADB connection and permissions.
- **Other errors:**
  - Check the `app.log` file for detailed error messages.

## License
MIT
