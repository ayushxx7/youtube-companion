"""YouTube Data API v3 client for fetching channel and video metrics."""

import os
import re
from datetime import datetime, timezone
from typing import Any, Optional

import isodate
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "@thevibecoder69")

_client = None


def _get_client():
    """Lazy-initialize the YouTube API client."""
    global _client
    if _client is None:
        if not YOUTUBE_API_KEY:
            raise ValueError(
                "YOUTUBE_API_KEY is not set. "
                "Copy .env.example to .env and add your API key."
            )
        _client = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    return _client


def _safe_int(stats: dict, key: str) -> Optional[int]:
    """Safely extract an integer stat. Returns None if the key is missing or 0.

    YouTube API omits likeCount/commentCount for some videos (e.g. shorts,
    videos with disabled likes). Returning None instead of 0 lets the UI
    distinguish "no data" from "zero".
    """
    val = stats.get(key)
    if val is None:
        return None
    try:
        n = int(val)
        return n if n > 0 else None
    except (ValueError, TypeError):
        return None


def _resolve_channel_id(client, channel_id_or_handle: str) -> str:
    """Resolve a handle (@name) or channel ID to a canonical channel ID."""
    # If it looks like a channel ID (UC...), return as-is
    if re.match(r"^UC[\w-]{22}$", channel_id_or_handle):
        return channel_id_or_handle

    # Try as a handle (with or without @)
    handle = channel_id_or_handle.lstrip("@")
    try:
        resp = (
            client.search()
            .list(q=f"@{handle}", type="channel", part="id", maxResults=1)
            .execute()
        )
        items = resp.get("items", [])
        if items:
            return items[0]["id"]["channelId"]
    except HttpError:
        pass

    # Try forUsername (legacy custom URL)
    try:
        resp = (
            client.channels()
            .list(part="id", forUsername=handle, maxResults=1)
            .execute()
        )
        items = resp.get("items", [])
        if items:
            return items[0]["id"]
    except HttpError:
        pass

    raise ValueError(
        f"Could not resolve channel: {channel_id_or_handle}. "
        "Try using the channel ID directly (UC...)."
    )


def get_channel_info(channel_id: Optional[str] = None) -> dict[str, Any]:
    """Fetch channel metadata and statistics."""
    client = _get_client()
    cid = _resolve_channel_id(client, channel_id or YOUTUBE_CHANNEL_ID)

    resp = (
        client.channels()
        .list(
            part="snippet,statistics,contentDetails,brandingSettings",
            id=cid,
        )
        .execute()
    )

    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Channel not found: {cid}")

    ch = items[0]
    snippet = ch.get("snippet", {})
    stats = ch.get("statistics", {})
    branding = ch.get("brandingSettings", {}).get("channel", {})

    return {
        "id": cid,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "custom_url": snippet.get("customUrl", ""),
        "published_at": snippet.get("published_at", ""),
        "thumbnail": snippet.get("thumbnails", {})
        .get("high", snippet.get("thumbnails", {}).get("default", {}))
        .get("url", ""),
        "country": snippet.get("country", ""),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "keywords": branding.get("keywords", ""),
    }


def get_playlist_videos(
    playlist_id: str, max_results: int = 50
) -> list[dict[str, Any]]:
    """Fetch all video IDs from a playlist (handles pagination)."""
    client = _get_client()
    video_ids = []
    next_page = None

    while len(video_ids) < max_results:
        batch = min(50, max_results - len(video_ids))
        resp = (
            client.playlistItems()
            .list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=batch,
                pageToken=next_page,
            )
            .execute()
        )
        for item in resp.get("items", []):
            vid = item.get("snippet", {}).get("resourceId", {}).get("videoId")
            if vid:
                video_ids.append(vid)
        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    return video_ids


def get_videos_details(
    video_ids: list[str],
) -> list[dict[str, Any]]:
    """Fetch details for a list of video IDs (batches of 50)."""
    client = _get_client()
    all_videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = (
            client.videos()
            .list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch),
            )
            .execute()
        )
        for item in resp.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            details = item.get("contentDetails", {})
            duration_iso = details.get("duration", "PT0S")

            views = _safe_int(stats, "viewCount")
            likes = _safe_int(stats, "likeCount")
            comments = _safe_int(stats, "commentCount")

            # Ratios: only compute if we have both numerator and denominator
            like_view_ratio = (likes / views) if (likes is not None and views is not None) else None
            comment_view_ratio = (comments / views) if (comments is not None and views is not None) else None

            all_videos.append(
                {
                    "id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:300],
                    "published_at": snippet.get("publishedAt", ""),
                    "thumbnail": snippet.get("thumbnails", {})
                    .get("high", snippet.get("thumbnails", {}).get("default", {}))
                    .get("url", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "tags": snippet.get("tags", []),
                    "category_id": snippet.get("categoryId", ""),
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "duration": duration_iso,
                    "duration_seconds": isodate.parse_duration(duration_iso).total_seconds(),
                    "like_view_ratio": like_view_ratio,
                    "comment_view_ratio": comment_view_ratio,
                }
            )

    return all_videos


def get_channel_videos(
    channel_id: Optional[str] = None, max_results: int = 50
) -> list[dict[str, Any]]:
    """Fetch recent videos from a channel (uses uploads playlist)."""
    client = _get_client()
    cid = _resolve_channel_id(client, channel_id or YOUTUBE_CHANNEL_ID)

    # Get the uploads playlist ID
    resp = (
        client.channels()
        .list(part="contentDetails", id=cid)
        .execute()
    )
    items = resp.get("items", [])
    if not items:
        return []

    uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids = get_playlist_videos(uploads_playlist, max_results)
    return get_videos_details(video_ids)


def get_channel_videos_df(
    channel_id: Optional[str] = None, max_results: int = 50
) -> pd.DataFrame:
    """Fetch channel videos and return as a DataFrame."""
    videos = get_channel_videos(channel_id, max_results)
    if not videos:
        return pd.DataFrame()

    df = pd.DataFrame(videos)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    df = df.sort_values("published_at", ascending=False)
    return df


def format_number(n: int) -> str:
    """Format large numbers: 1234567 → '1.23M', 1234 → '1.23K'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_duration(seconds: float) -> str:
    """Format seconds to MM:SS or HH:MM:SS."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
