import random
from datetime import datetime, timedelta
from db.database import Base, engine, SessionLocal
from db.models import Video, DailyMetric, RetentionData, VideoType

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(Video).first():
        db.close()
        print("Database already seeded.")
        return

    sample_videos = [
        ("vid_001", "I Built an AI Office with 12 Agents", VideoType.long, 15200, "78%", "92", "12.4", "5.2%",
         "Strong hook but CTR could improve. Try Thumbnail Variant B with a shocked face close-up."),
        ("vid_002", "MCP Servers Explained in 60 Seconds", VideoType.short, 45000, "65%", "110", "8.2", "8.1%",
         "Excellent packaging. The title/thumbnail combo is driving high CTR. Double down on MCP content."),
        ("vid_003", "Why Streamlit is Perfect for AI Tools", VideoType.long, 8300, "81%", "75", "15.1", "3.8%",
         "Low views but high engagement. Algorithm hasn't picked it up yet. Share on Reddit/HN for initial push."),
        ("vid_004", "AI Agent Automates My Entire YouTube Workflow", VideoType.short, 67000, "72%", "135", "6.5", "9.4%",
         "Viral potential confirmed. Highest CTR in the catalog. Make a part 2 asap."),
        ("vid_005", "Hermes vs Claude Code: Which is Better?", VideoType.long, 12000, "55%", "68", "9.8", "4.1%",
         "Hook needs work — 45% drop-off in first 3 seconds. Start with a bold claim or surprising demo."),
    ]

    for vid in sample_videos:
        video = Video(
            id=vid[0], title=vid[1], video_type=vid[2], total_views=vid[3],
            hook_score=vid[4], packaging_score=vid[5], engagement_efficiency=vid[6],
            avg_ctr=vid[7], recommendation=vid[8]
        )
        db.add(video)

        # Add daily metrics
        for i in range(14):
            date = datetime.today() - timedelta(days=13 - i)
            db.add(DailyMetric(
                video_id=vid[0], date=date,
                views=random.randint(100, 2000),
                likes=random.randint(5, 100),
                comments=random.randint(0, 30)
            ))

        # Add retention curve data
        for sec in range(0, 65, 5):
            retention = max(5, 100 - sec * 1.2 + random.uniform(-5, 5))
            db.add(RetentionData(
                video_id=vid[0], timestamp_seconds=sec,
                retention_percentage=round(retention, 1)
            ))

    db.commit()
    db.close()
    print("Seeded database with demo data.")

if __name__ == "__main__":
    seed()
