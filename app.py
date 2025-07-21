import streamlit as st
import os
import json
import requests
import tempfile
from typing import Dict, List, Optional
import time
import pickle

import speech_recognition as sr
from moviepy.video.io.VideoFileClip import VideoFileClip

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secrets.json"
class VoiceRecorder:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def calibrate_microphone(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def record_voice(self, timeout: int = 25, phrase_timeout: int = 2) -> str:
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_timeout)
            st.info("🔄 Processing speech...")
            return self.recognizer.recognize_google(audio)
        except sr.RequestError as e:
            st.warning(f"Google Speech API error: {e}")
            return ""
        except sr.UnknownValueError:
            st.warning("Could not understand the audio.")
            return ""
        except Exception as e:
            st.error(f"Voice recording error: {e}")
            return ""

class AIMetadataGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL

    def generate_metadata(self, voice_notes: str, video_info: Dict) -> Dict:
        prompt = f"""
        Based on the following voice notes about a YouTube video, generate comprehensive metadata:
        Voice Notes: {voice_notes}
        Video Info: Duration: {video_info.get('duration', 'Unknown')}, Size: {video_info.get('size', 'Unknown')}
        Please provide:
        1. Three compelling title options (each under 60 characters)
        2. A detailed description (200-300 words)
        3. 15 relevant hashtags categorized as:
           - Content type
           - Topic relevance 
           - Trending/discoverable
        Format your response as JSON.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a YouTube metadata expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            return json.loads(content[json_start:json_end])
        except Exception as e:
            st.error(f"Metadata generation error: {e}")
            return self._get_fallback_metadata()

    def _get_fallback_metadata(self) -> Dict:
        return {
            "titles": ["Amazing Video", "Must Watch", "Incredible Content"],
            "description": "This is an awesome video. Watch and enjoy!",
            "hashtags": {
                "content_type": ["#video", "#content"],
                "topic_relevant": ["#youtube", "#ai"],
                "trending": ["#2025", "#viral"]
            }
        }
class YouTubeUploader:
    def __init__(self):
        self.youtube_service = None
        self.credentials = None

    def authenticate(self) -> bool:
        try:
            if os.path.exists('youtube_credentials.pickle'):
                with open('youtube_credentials.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(CLIENT_SECRETS_FILE):
                        st.error("Missing client_secrets.json")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                    self.credentials = flow.run_local_server(port=0)

                    with open('youtube_credentials.pickle', 'wb') as token:
                        pickle.dump(self.credentials, token)

            self.youtube_service = build('youtube', 'v3', credentials=self.credentials)
            return True

        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return False

    def upload_video(self, video_file, title: str, description: str, tags: List[str], privacy_status: str = "private") -> Optional[str]:
        if not self.youtube_service:
            st.error("YouTube not authenticated.")
            return None

        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(video_file.name, resumable=True)
            upload_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            progress_bar = st.progress(0)
            status_text = st.empty()

            response = None
            while response is None:
                status, response = upload_request.next_chunk()
                if status:
                    percent = int(status.progress() * 100)
                    progress_bar.progress(percent)
                    status_text.text(f"Upload progress: {percent}%")

            if response:
                video_id = response.get("id")
                st.success(f"Upload complete! Video ID: {video_id}")
                st.write(f"https://www.youtube.com/watch?v={video_id}")
                return video_id

        except Exception as e:
            st.error(f"Upload error: {e}")
class VideoProcessor:
    @staticmethod
    def get_video_info(video_file) -> Dict:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(video_file.read())
                tmp_path = tmp_file.name

            with VideoFileClip(tmp_path) as video:
                duration = video.duration
                size = os.path.getsize(tmp_path)
                fps = video.fps
                resolution = f"{video.w}x{video.h}"

            os.unlink(tmp_path)
            return {
                'duration': f"{int(duration//60)}:{int(duration%60):02d}",
                'size': f"{size / (1024*1024):.1f} MB",
                'fps': fps,
                'resolution': resolution
            }
        except Exception as e:
            st.error(f"Video processing failed: {e}")
            return {
                'duration': 'Unknown',
                'size': 'Unknown',
                'fps': 'Unknown',
                'resolution': 'Unknown'
            }

def initialize_session_state():
    st.session_state.setdefault('voice_notes', "")
    st.session_state.setdefault('generated_metadata', None)
    st.session_state.setdefault('selected_title', "")
    st.session_state.setdefault('final_description', "")
    st.session_state.setdefault('final_tags', [])
    st.session_state.setdefault('youtube_authenticated', False)
    if 'youtube_uploader' not in st.session_state:
        st.session_state.youtube_uploader = YouTubeUploader()
def main():
    st.set_page_config(page_title="YouTube Upload Assistant", page_icon="🎥", layout="wide")
    initialize_session_state()

    voice_recorder = VoiceRecorder()
    ai_generator = AIMetadataGenerator(OPENROUTER_API_KEY)
    youtube_uploader = st.session_state.youtube_uploader

    st.title("🎥 YouTube Upload Assistant")
    st.markdown("Upload videos with AI-generated metadata and voice support!")

    with st.sidebar:
        st.header("⚙️ Configuration")
        st.selectbox("Theme", ["Light", "Dark"])
        st.subheader("🔑 YouTube Authentication")
        if st.button("Authenticate with YouTube"):
            if youtube_uploader.authenticate():
                st.session_state.youtube_authenticated = True
                st.success("✅ Authenticated with YouTube!")
            else:
                st.error("❌ Authentication failed")

        if st.session_state.youtube_authenticated:
            st.success("YouTube is ready ✅")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📁 Upload Video")
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi', 'mkv'])
        if uploaded_file:
            info = VideoProcessor.get_video_info(uploaded_file)
            st.metric("Duration", info['duration'])
            st.metric("Size", info['size'])
            st.metric("Resolution", info['resolution'])
            st.video(uploaded_file)

    with col2:
        st.header("🎤 Voice Notes")
        if st.button("🎙️ Record Voice"):
            voice_recorder.calibrate_microphone()
            transcribed = voice_recorder.record_voice(timeout=10, phrase_timeout=5)
            if transcribed:
                st.session_state.voice_notes += " " + transcribed
                st.success("Note added.")
        if st.button("🗑️ Clear Notes"):
            st.session_state.voice_notes = ""

        st.session_state.voice_notes = st.text_area("Notes", st.session_state.voice_notes, height=150)

        if st.button("✨ Generate Metadata"):
            if st.session_state.voice_notes and uploaded_file:
                with st.spinner("Generating..."):
                    info = VideoProcessor.get_video_info(uploaded_file)
                    metadata = ai_generator.generate_metadata(st.session_state.voice_notes, info)
                    st.session_state.generated_metadata = metadata
                st.success("Metadata generated!")
            else:
                st.warning("Please upload a video and enter notes.")

    if st.session_state.generated_metadata:
        md = st.session_state.generated_metadata
        st.header("📝 Review Metadata")
        titles = md.get('titles', [])
        idx = st.radio("Select a title", range(len(titles)), format_func=lambda i: titles[i])
        st.session_state.selected_title = titles[idx]
        st.session_state.final_description = st.text_area("Description", md.get("description", ""), height=200)
        hashtags = md.get("hashtags", {})
        all_tags = []
        for cat, tags in hashtags.items():
            st.write(f"**{cat.title()}**: {' '.join(tags)}")
            all_tags.extend(tags)
        custom = st.text_input("Add custom tags (comma-separated):")
        if custom:
            all_tags.extend([f"#{tag.strip()}" for tag in custom.split(',')])
        st.session_state.final_tags = all_tags
    if uploaded_file and st.session_state.generated_metadata:
        st.header("🚀 Upload")

        privacy = st.selectbox("Privacy", ["private", "unlisted", "public"])

        if st.button("📤 Upload to YouTube"):
            if not st.session_state.youtube_authenticated:
                st.error("❌ Please authenticate with YouTube first.")
            else:
                if not youtube_uploader.youtube_service:
                    st.error("❌ YouTube service not initialized.")
                    st.info("Try re-authenticating.")
                else:
                    with st.spinner("Uploading to YouTube..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                                tmp.write(uploaded_file.getbuffer())
                                tmp.flush()
                                video_id = youtube_uploader.upload_video(
                                    tmp,
                                    st.session_state.selected_title,
                                    st.session_state.final_description,
                                    [tag.strip("#") for tag in st.session_state.final_tags],
                                    privacy
                                )
                            os.unlink(tmp.name)
                            if video_id:
                                st.balloons()
                                st.success("🎉 Video uploaded successfully!")
                        except Exception as e:
                            st.error(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    main()
