from fastmcp import FastMCP
from db.database import SessionLocal
from core.intelligence import IntelligenceEngine
import pandas as pd

mcp = FastMCP("VibeIntelligence")

@mcp.tool(app=True)
def analyze_video_performance(video_id: str):
    """
    Detailed performance analysis for a video. Returns an interactive dashboard card.
    """
    db = SessionLocal()
    try:
        engine = IntelligenceEngine(db)
        analysis = engine.get_video_kpis(video_id)
        
        if not analysis:
            return f"Video {video_id} not found."

        return {
            "type": "PrefabApp",
            "title": f"Deep Dive: {analysis['title']}",
            "components": [
                {"type": "Metric", "label": "Packaging Efficiency", "value": analysis['packaging_score'], "status": "good" if float(analysis['packaging_score']) > 80 else "bad"},
                {"type": "Metric", "label": "Hook Quality", "value": analysis['hook_score'], "status": "good" if float(analysis['hook_score'].strip('%')) > 65 else "bad"},
                {"type": "Callout", "title": "AI Insight", "text": analysis['recommendation'], "variant": "info"},
                {"type": "Table", "headers": ["Stat", "Value"], "rows": [
                    ["Views", f"{analysis['total_views']:,}"],
                    ["Engagement Rate", analysis['engagement_efficiency']],
                    ["Status", analysis['status']]
                ]}
            ]
        }
    finally:
        db.close()

@mcp.tool(app=True)
def compare_videos(video_id_1: str, video_id_2: str):
    """
    Side-by-side comparison of two videos.
    """
    db = SessionLocal()
    try:
        engine = IntelligenceEngine(db)
        v1 = engine.get_video_kpis(video_id_1)
        v2 = engine.get_video_kpis(video_id_2)
        
        return {
            "type": "PrefabApp",
            "title": "Video Comparison",
            "components": [
                {"type": "Table", "headers": ["Metric", v1['title'][:20], v2['title'][:20]], "rows": [
                    ["Views", str(v1['total_views']), str(v2['total_views'])],
                    ["Packaging", v1['packaging_score'], v2['packaging_score']],
                    ["Hook", v1['hook_score'], v2['hook_score']],
                    ["Eng. Efficiency", v1['engagement_efficiency'], v2['engagement_efficiency']]
                ]},
                {"type": "Callout", "title": "Winner", "text": f"{v1['title'] if v1['total_views'] > v2['total_views'] else v2['title']} has higher reach.", "variant": "success"}
            ]
        }
    finally:
        db.close()

@mcp.tool()
def list_my_videos():
    """Returns a list of all videos with their IDs for analysis."""
    db = SessionLocal()
    try:
        engine = IntelligenceEngine(db)
        overview = engine.get_channel_overview()
        return [{"id": v['id'], "title": v['title'], "views": v['total_views']} for v in overview]
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
