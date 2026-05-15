# 🚀 VibeIntelligence: YouTube Creator Intelligence

A personal analytics system built for @thevibecoder69 using **FastMCP 3.2** and **Streamlit**.

## Features
- **FastMCP 3.2 Apps**: Interactive AI-driven performance cards (`analyze_video_performance`).
- **Intelligence Engine**: Custom KPIs like **Hook Score** (3s retention) and **Packaging Score** (CTR efficiency).
- **Premium Dashboard**: Dark-mode analytics with Plotly visualizations.
- **Shorts Focus**: Specific logic for swipe-away behavior and short-form engagement.
- **AI Recommendations**: Actionable advice based on video outlier analysis.

## Setup

1. **Quick Start (Demo Mode):**
   ```bash
   cd analytics-intelligence
   python setup.py
   ```

2. **Run Dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

3. **Run MCP Server:**
   ```bash
   python mcp_server.py
   ```

## Architecture
- **Backend**: Python (FastAPI/FastMCP)
- **Intelligence**: Pandas + SQLAlchemy
- **Database**: SQLite (local persistence)
- **Frontend**: Streamlit (Premium Theme)

## Metric Formulas
- **Hook Score**: Retention at 3 seconds.
- **Packaging Score**: (Actual CTR / Target CTR) * 100. Target is normalized by content type (Short vs Long).
- **Engagement Efficiency**: Likes per 1000 views.

## Real Data Integration
To connect your own channel:
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable YouTube Data, Analytics, and Reporting APIs.
3. Download `client_secrets.json` and place it in the root directory.
4. The system will handle the OAuth2 flow on the first run.
