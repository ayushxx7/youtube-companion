# Yt_Uploader

# YouTube Upload Assistant - Setup Guide

## Requirements (requirements.txt)

```txt
streamlit>=1.32.0
SpeechRecognition>=3.10.0
moviepy>=1.0.3
google-auth>=2.17.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.85.0
requests>=2.28.0
pyaudio>=0.2.11
```

## Installation Steps

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv youtube_uploader_env

# Activate environment
# Windows:
youtube_uploader_env\Scripts\activate
# Linux/Mac:
source youtube_uploader_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google API Setup

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3

2. **Create OAuth 2.0 Credentials:**
   - Go to Credentials section
   - Create credentials → OAuth client ID
   - Choose "Desktop application"
   - Download the JSON file and rename it to `client_secrets.json`
   - Place it in your app directory

3. **Configure OAuth Consent Screen:**
   - Add your email to test users
   - Set scopes: `https://www.googleapis.com/auth/youtube.upload`

### 3. OpenRouter API Setup

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Set environment variable:

```bash
# Windows:
set OPENROUTER_API_KEY=your_api_key_here

# Linux/Mac:
export OPENROUTER_API_KEY=your_api_key_here
```

### 4. Audio Setup (Important!)

**Windows:**
- PyAudio should install automatically
- If issues occur, install from wheel: 
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```

**Linux:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

### 5. File Structure

```
youtube_uploader/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── client_secrets.json       # Google OAuth credentials (you provide)
├── youtube_credentials.pickle # Auto-generated after auth
└── README.md                # This file
```

## Running the Application

```bash
streamlit run app.py
```

## Usage Guide

### 1. Initial Setup
- Set OpenRouter API key in environment
- Add `client_secrets.json` from Google Cloud Console
- Authenticate with YouTube (one-time setup)

### 2. Upload Workflow
1. **Upload Video**: Choose your video file
2. **Voice Notes**: Click "Record Voice Notes" and speak about your video
3. **Generate Metadata**: Click "Generate AI Metadata" 
4. **Review & Edit**: Select title, edit description, review hashtags
5. **Upload**: Choose privacy setting and upload to YouTube

### 3. Voice Commands Tips
- Speak clearly at normal pace
- Mention key topics, themes, target audience
- Describe video style, genre, mood
- Include any special instructions for titles/descriptions

## Features

### ✅ Implemented Features
- Video file upload with preview
- Voice-to-text recording
- AI metadata generation (titles, descriptions, hashtags)
- YouTube API integration with OAuth
- Progress tracking for uploads
- Session state management
- Error handling and user feedback

### 🔄 Advanced Features
- **Privacy Controls**: Public, unlisted, private options
- **Metadata Templates**: Save and reuse common formats
- **Category Selection**: Auto-categorization based on content
- **Hashtag Intelligence**: Categorized by type (content, topic, trending)
- **Progress Indicators**: Real-time upload progress
- **Responsive Design**: Works on desktop and mobile

## Troubleshooting

### Common Issues

1. **"No module named 'pyaudio'"**
   - Follow audio setup instructions above
   - Try: `pip install --upgrade pyaudio`

2. **Google API Authentication Errors**
   - Ensure `client_secrets.json` is in app directory
   - Check OAuth consent screen configuration
   - Verify YouTube Data API is enabled

3. **OpenRouter API Errors**
   - Verify API key is set correctly
   - Check account has sufficient credits
   - Ensure internet connection for API calls

4. **Voice Recognition Issues**
   - Check microphone permissions
   - Try calibrating microphone (auto-calibrated on first use)
   - Ensure quiet environment for recording

### Performance Tips

1. **Large Video Files**: 
   - Keep under 128MB for faster processing
   - Use compressed formats (MP4 recommended)

2. **API Quotas**:
   - YouTube API has daily quotas
   - OpenRouter has rate limits
   - App includes retry logic for failed requests

3. **Memory Usage**:
   - Large videos processed in chunks
   - Temporary files cleaned automatically

## API Costs

- **Google YouTube API**: Free (with quotas)
- **OpenRouter API**: Pay per use (~$0.001 per generation)
- **Speech Recognition**: Free (Google Web Speech API)

## Privacy & Security

- OAuth tokens stored locally only
- No user data sent to third parties (except APIs)
- Voice recordings processed locally
- Video files not stored permanently

## Future Enhancements

- [ ] Thumbnail generation and upload
- [ ] End screen template application  
- [ ] A/B testing for titles
- [ ] YouTube Analytics integration
- [ ] Batch upload capabilities
- [ ] Custom AI prompts for metadata
- [ ] Video editing basic features
- [ ] Schedule publishing
- [ ] Multi-language support

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify all setup steps completed
3. Check GitHub issues/discussions
4. Review API documentation for Google/OpenRouter
