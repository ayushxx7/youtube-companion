import pandas as pd
from db.database import SessionLocal
from db.models import Video, DailyMetric, RetentionData

class IntelligenceEngine:
    def __init__(self, db):
        self.db = db

    def get_channel_overview(self):
        videos = self.db.query(Video).all()
        overview = []
        for v in videos:
            overview.append({
                "id": v.id,
                "title": v.title,
                "status": v.status,
                "type": v.video_type.value,
                "total_views": v.total_views,
                "hook_score": v.hook_score,
                "packaging_score": v.packaging_score,
                "engagement_efficiency": v.engagement_efficiency,
                "avg_ctr": v.avg_ctr,
                "recommendation": v.recommendation,
            })
        return overview

    def get_video_kpis(self, video_id: str):
        v = self.db.query(Video).filter(Video.id == video_id).first()
        if not v:
            return None
        return {
            "id": v.id,
            "title": v.title,
            "status": v.status,
            "type": v.video_type.value,
            "total_views": v.total_views,
            "hook_score": v.hook_score,
            "packaging_score": v.packaging_score,
            "engagement_efficiency": v.engagement_efficiency,
            "avg_ctr": v.avg_ctr,
            "recommendation": v.recommendation,
        }
