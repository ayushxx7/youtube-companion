import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Video, DailyMetric, RetentionData, VideoType
from core.intelligence import IntelligenceEngine

st.set_page_config(page_title="VibeIntelligence Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4150; }
    .stCard { background-color: #1e2130; padding: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    db = SessionLocal()
    engine = IntelligenceEngine(db)
    videos = db.query(Video).all()
    overview = engine.get_channel_overview()
    db.close()
    return videos, overview

videos, overview = load_data()
df_overview = pd.DataFrame(overview)

st.title("🚀 VibeIntelligence: @thevibecoder69")
st.subheader("Creator Intelligence System")

# Sidebar Filters
st.sidebar.title("Filters")
video_type = st.sidebar.multiselect("Content Type", options=["short", "long"], default=["short", "long"])
status_filter = st.sidebar.multiselect("Status", options=df_overview['status'].unique(), default=df_overview['status'].unique())

filtered_df = df_overview[(df_overview['type'].isin(video_type)) & (df_overview['status'].isin(status_filter))]

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Videos", len(filtered_df))
with col2:
    st.metric("Total Views", f"{filtered_df['total_views'].sum():,}")
with col3:
    st.metric("Avg Hook Score", f"{pd.to_numeric(filtered_df['hook_score'].str.strip('%')).mean():.1f}%")
with col4:
    st.metric("Avg Packaging", f"{pd.to_numeric(filtered_df['packaging_score']).mean():.1f}")

st.divider()

# Main Visuals
tab1, tab2, tab3 = st.tabs(["Performance Matrix", "Video Deep Dive", "Content Patterns"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Views vs Packaging Score")
        fig = px.scatter(filtered_df, x="packaging_score", y="total_views", size="total_views", 
                         color="status", hover_name="title", template="plotly_dark",
                         labels={"packaging_score": "Packaging Efficiency", "total_views": "Lifetime Views"})
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Hook Quality vs Engagement")
        # Convert types for plotting
        plot_df = filtered_df.copy()
        plot_df['hook_num'] = pd.to_numeric(plot_df['hook_score'].str.strip('%'))
        plot_df['engagement_num'] = pd.to_numeric(plot_df['engagement_efficiency'])
        
        fig = px.bar(plot_df, x="title", y="hook_num", color="engagement_num", 
                     template="plotly_dark", title="Retention Hook Quality by Video")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    selected_video_title = st.selectbox("Select Video for Deep Dive", options=filtered_df['title'].tolist())
    video_id = filtered_df[filtered_df['title'] == selected_video_title]['id'].values[0]
    
    db = SessionLocal()
    retention = db.query(RetentionData).filter(RetentionData.video_id == video_id).order_by(RetentionData.timestamp_seconds).all()
    daily = db.query(DailyMetric).filter(DailyMetric.video_id == video_id).order_by(DailyMetric.date).all()
    db.close()
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Audience Retention Curve")
        rd_df = pd.DataFrame([{'sec': r.timestamp_seconds, 'ret': r.retention_percentage} for r in retention])
        fig = px.line(rd_df, x='sec', y='ret', template="plotly_dark")
        fig.add_hline(y=50, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        v_analysis = filtered_df[filtered_df['id'] == video_id].iloc[0]
        st.info(f"**AI Recommendation:**\n\n{v_analysis['recommendation']}")
        st.write(f"**Status:** {v_analysis['status']}")
        st.write(f"**CTR:** {v_analysis['avg_ctr']}")
        st.write(f"**Eng. Efficiency:** {v_analysis['engagement_efficiency']}")

with tab3:
    st.subheader("Topic Cluster Analysis")
    cluster_performance = filtered_df.groupby('type')['total_views'].mean().reset_index()
    st.bar_chart(cluster_performance.set_index('type'))
    st.write("AI Suggestion: Your Shorts on 'AI/Coding' are outperforming 'Vlog' by 40%. Triple down on MCP server tutorials.")
