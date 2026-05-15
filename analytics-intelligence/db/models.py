from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from db.database import Base

class VideoType(enum.Enum):
    short = "short"
    long = "long"

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, default="published")
    video_type = Column(Enum(VideoType), default=VideoType.short)
    total_views = Column(Integer, default=0)
    hook_score = Column(String, default="0%")
    packaging_score = Column(String, default="0")
    engagement_efficiency = Column(String, default="0")
    avg_ctr = Column(String, default="0%")
    recommendation = Column(Text, default="No recommendation yet.")

    daily_metrics = relationship("DailyMetric", back_populates="video")
    retention_data = relationship("RetentionData", back_populates="video")

class DailyMetric(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("videos.id"))
    date = Column(Date)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    video = relationship("Video", back_populates="daily_metrics")

class RetentionData(Base):
    __tablename__ = "retention_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey("videos.id"))
    timestamp_seconds = Column(Integer)
    retention_percentage = Column(Float)

    video = relationship("Video", back_populates="retention_data")
