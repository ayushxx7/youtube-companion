"""YouTube Channel Dashboard for @thevibecoder69 — built with Streamlit."""

import os
import pathlib
import sys
from typing import Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── Load env ──────────────────────────────────────────────────────────────
load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────
_FAVICON = str(pathlib.Path(__file__).parent / "favicon.png")

st.set_page_config(
    page_title="The Vibe Coder — YouTube Dashboard",
    page_icon=_FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #3d3d5c;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .metric-card:hover {
        border-color: #ff6b6b;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ff6b6b;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a0a0b0;
        margin-top: 4px;
    }
    .video-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #3d3d5c;
        margin-bottom: 12px;
    }
    .video-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e0e0f0;
    }
    .video-stats {
        font-size: 0.8rem;
        color: #a0a0b0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    a.metric-link {
        text-decoration: none;
        color: inherit;
        display: block;
    }
    a.metric-link:hover {
        text-decoration: none;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────
def metric_card(label: str, value: str, delta: Optional[str] = None, video_id: Optional[str] = None):
    """Render a styled metric card. If video_id is provided, clicking opens the YouTube video."""
    delta_html = (
        f'<div style="color: {"#4caf50" if delta and not delta.startswith("−") else "#f44336"}; font-size: 0.8rem;">{delta}</div>'
        if delta
        else ""
    )

    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        card_html = f"""
        <div class="metric-card" onclick="window.open('{url}', '_blank')" style="cursor: pointer;">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """
    else:
        card_html = f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """

    st.markdown(card_html, unsafe_allow_html=True)


def embed_video(video_id: str, width: int = 320, height: int = 180):
    """Render an embedded YouTube video iframe."""
    st.markdown(
        f"""
        <iframe width="{width}" height="{height}"
            src="https://www.youtube.com/embed/{video_id}"
            title="YouTube video player" frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            style="border-radius: 8px;">
        </iframe>
        """,
        unsafe_allow_html=True,
    )


def video_card(video: dict, expand_desc: bool = False):
    """Render a single video card with embedded player."""
    vid = video.get("id", "")
    title = video.get("title", "Untitled")
    url = f"https://www.youtube.com/watch?v={vid}"

    # Title is a clickable link
    views_val = video.get("views")
    likes_val = video.get("likes")
    comments_val = video.get("comments")
    views_d = f"{int(views_val):,}" if pd.notna(views_val) else "0"
    likes_d = f"{int(likes_val):,}" if pd.notna(likes_val) else "N/A"
    comments_d = f"{int(comments_val):,}" if pd.notna(comments_val) else "N/A"
    st.markdown(
        f"""
        <div class="video-card">
            <div class="video-title"><a href="{url}" target="_blank" style="color: #e0aaff; text-decoration: none;">{title}</a></div>
            <div class="video-stats">
                👁 {views_d} views &nbsp;|&nbsp;
                👍 {likes_d} &nbsp;|&nbsp;
                💬 {comments_d} &nbsp;|&nbsp;
                ⏱ {video.get("duration_formatted", "N/A")} &nbsp;|&nbsp;
                📅 {video.get("published_formatted", "N/A")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Embedded video player
    if vid:
        embed_video(vid, width=400, height=225)

    desc = video.get("description", "")
    if desc:
        with st.expander("Description"):
            st.write(desc)
    st.markdown("---")


def video_table_row(video: dict):
    """Render a video as a table row with embedded thumbnail that links to video."""
    vid = video.get("id", "")
    url = f"https://www.youtube.com/watch?v={vid}"
    thumb = video.get("thumbnail", "")
    title = video.get("title", "Untitled")
    views = video.get("views", 0)
    likes = video.get("likes", 0)
    comments = video.get("comments", 0)
    published = video.get("published_at", "")
    if hasattr(published, "strftime"):
        published = published.strftime("%Y-%m-%d")

    # Show thumbnail image linking to video
    if thumb:
        st.markdown(
            f'<a href="{url}" target="_blank"><img src="{thumb}" width="120" style="border-radius: 6px;"></a>',
            unsafe_allow_html=True,
        )
    st.markdown(f"[{title}]({url})")
    st.caption(f"👁 {views:,} | 👍 {likes:,} | 💬 {comments:,} | 📅 {published}")


# ── Data loading (moved after sidebar for slider access) ──────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_data(channel_id: str, max_v: int):
    """Load channel info and videos with caching."""
    from yt_api import get_channel_info, get_channel_videos_df

    channel = get_channel_info(channel_id)
    videos_df = get_channel_videos_df(channel_id, max_v)
    return channel, videos_df


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    # Channel thumbnail — use the API-fetched one; fall back to a styled placeholder
    # Note: channel may not be loaded yet on first render, so check globals
    _ch = globals().get("channel", {})
    _thumb_url = _ch.get("thumbnail", "") if isinstance(_ch, dict) else ""
    if _thumb_url:
        st.image(_thumb_url, width=120, use_container_width=False)
    else:
        st.markdown(
            "<div style='width:120px;height:120px;background:linear-gradient(135deg,#ff6b6b,#e0aaff);"
            "border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2.5rem;'>"
            "🎬</div>",
            unsafe_allow_html=True,
        )
    st.title("🎬 YT Dashboard")
    st.caption("The Vibe Coder — @thevibecoder69")

    st.divider()

    view = st.radio(
        "Dashboard View",
        ["📊 Public Overview", "🎥 Video Explorer", "📈 Analytics", "🔐 Studio (Coming Soon)"],
        index=0,
    )

    st.divider()

    with st.expander("⚙️ Settings"):
        api_key_input = st.text_input(
            "YouTube API Key",
            value=os.getenv("YOUTUBE_API_KEY", ""),
            type="password",
            help="Get one at console.cloud.google.com/apis/credentials",
        )
        if api_key_input:
            os.environ["YOUTUBE_API_KEY"] = api_key_input

        channel_input = st.text_input(
            "Channel",
            value=os.getenv("YOUTUBE_CHANNEL_ID", "@thevibecoder69"),
            help="Handle (@name) or Channel ID (UC...)",
        )
        if channel_input:
            os.environ["YOUTUBE_CHANNEL_ID"] = channel_input

        max_videos = st.slider("Max videos to fetch", 10, 100, 50)

    st.divider()
    st.caption("Built with ❤️ by The Office team")


# ── Data loading ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_data(channel_id: str, max_v: int):
    """Load channel info and videos with caching."""
    from yt_api import get_channel_info, get_channel_videos_df

    channel = get_channel_info(channel_id)
    videos_df = get_channel_videos_df(channel_id, max_v)
    return channel, videos_df


# ── Main content ──────────────────────────────────────────────────────────
try:
    channel, videos_df = load_data(
        os.getenv("YOUTUBE_CHANNEL_ID", "@thevibecoder69"),
        max_videos,
    )
except ValueError as e:
    st.error(f"⚠️ {e}")
    st.info(
        "👈 Set your YouTube API Key in the sidebar. "
        "Get one free at https://console.cloud.google.com/apis/credentials"
    )
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ── Channel header ────────────────────────────────────────────────────────
col_thumb, col_info = st.columns([1, 5])
with col_thumb:
    _header_thumb = channel.get("thumbnail", "") if isinstance(channel, dict) else ""
    if _header_thumb:
        st.image(_header_thumb, width=120, use_container_width=False, output_format="PNG")
    else:
        st.markdown(
            "<div style='width:120px;height:120px;background:linear-gradient(135deg,#ff6b6b,#e0aaff);"
            "border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2.5rem;'>"
            "🎬</div>",
            unsafe_allow_html=True,
        )
with col_info:
    st.title(f"🎬 {channel['title']}")
    if channel.get("custom_url"):
        st.caption(f"youtube.com/{channel['custom_url']}")
    desc = channel.get("description", "")
    if desc:
        with st.expander("Channel Description"):
            st.write(desc)

st.divider()

# ── Determine the top video for clickable metrics ─────────────────────────
top_video_id = None
if not videos_df.empty and "id" in videos_df.columns:
    top_idx = videos_df["views"].idxmax()
    top_video_id = videos_df.loc[top_idx, "id"]

# ── View routing ──────────────────────────────────────────────────────────
if view == "📊 Public Overview":
    # ── Key metrics row ───────────────────────────────────────────────────
    # Each metric card is clickable and opens the top video on YouTube
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Subscribers", f"{channel['subscriber_count']:,}", video_id=top_video_id)
    with m2:
        metric_card("Total Views", f"{channel['view_count']:,}", video_id=top_video_id)
    with m3:
        metric_card("Videos", f"{channel['video_count']:,}", video_id=top_video_id)
    with m4:
        avg_views = (
            int(videos_df["views"].mean()) if not videos_df.empty else 0
        )
        metric_card("Avg Views/Video", f"{avg_views:,}", video_id=top_video_id)

    st.divider()

    # ── Video performance table with embedded videos ───────────────────────
    if not videos_df.empty:
        st.subheader("📋 Recent Videos Performance")

        for _, row in videos_df.sort_values("published_at", ascending=False).iterrows():
            video = row.to_dict()
            vid = video.get("id", "")
            url = f"https://www.youtube.com/watch?v={vid}"
            title = video.get("title", "Untitled")
            views = video.get("views")
            likes = video.get("likes")
            comments = video.get("comments")
            like_ratio = video.get("like_view_ratio")
            comment_ratio = video.get("comment_view_ratio")
            published_at = video.get("published_at")
            thumb = video.get("thumbnail", "")

            pub_str = (
                published_at.strftime("%b %d, %Y")
                if pd.notna(published_at)
                else "N/A"
            )
            views_str = f"{views:,}" if pd.notna(views) else "N/A"
            likes_str = f"{likes:,}" if pd.notna(likes) else "N/A"
            comments_str = f"{comments:,}" if pd.notna(comments) else "N/A"
            like_ratio_str = f"{like_ratio:.2%}" if pd.notna(like_ratio) else "N/A"
            comment_ratio_str = f"{comment_ratio:.2%}" if pd.notna(comment_ratio) else "N/A"

            col_embed, col_meta = st.columns([1, 2])
            with col_embed:
                if vid:
                    embed_video(vid, width=240, height=135)
                elif thumb:
                    st.markdown(
                        f'<a href="{url}" target="_blank"><img src="{thumb}" width="240" style="border-radius:8px;"></a>',
                        unsafe_allow_html=True,
                    )
            with col_meta:
                st.markdown(f"### [{title}]({url})")
                st.caption(
                    f"👁 {views_str} views &nbsp;|&nbsp; "
                    f"👍 {likes_str} &nbsp;|&nbsp; "
                    f"💬 {comments_str} &nbsp;|&nbsp; "
                    f"📊 {like_ratio_str} like/view &nbsp;|&nbsp; "
                    f"💭 {comment_ratio_str} comment/view &nbsp;|&nbsp; "
                    f"📅 {pub_str}"
                )
            st.divider()

        # ── Top videos chart ──────────────────────────────────────────────
        st.subheader("🏆 Top 10 Videos by Views")
        top10 = videos_df.nlargest(10, "views")[["id", "title", "views"]].copy()
        # Make titles clickable
        top10["Title"] = top10.apply(
            lambda row: f"[{row['title'][:40]}](https://www.youtube.com/watch?v={row['id']})",
            axis=1,
        )
        chart_data = top10[["Title", "views"]].set_index("Title")
        st.bar_chart(chart_data, use_container_width=True)

        # ── Engagement scatter with video titles on hover ─────────────────
        st.subheader("💡 Engagement Overview")
        st.caption("Hover over points to see video titles. Click to open on YouTube.")

        # Use Altair for proper hover tooltips with video names
        import altair as alt

        scatter_data = videos_df[["views", "likes", "title", "id"]].copy()
        scatter_data["url"] = scatter_data["id"].apply(
            lambda x: f"https://www.youtube.com/watch?v={x}"
        )
        scatter_data["title_short"] = scatter_data["title"].str[:40]

        chart = (
            alt.Chart(scatter_data)
            .mark_circle(size=80, opacity=0.7)
            .encode(
                x=alt.X("views:Q", title="Views"),
                y=alt.Y("likes:Q", title="Likes"),
                tooltip=[
                    alt.Tooltip("title_short:N", title="Video"),
                    alt.Tooltip("views:Q", title="Views", format=","),
                    alt.Tooltip("likes:Q", title="Likes", format=","),
                ],
                href="url:N",
                color=alt.Color("likes:Q", scale=alt.Scale(scheme="reds"), legend=None),
            )
            .interactive()
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No videos found for this channel.")

elif view == "🎥 Video Explorer":
    # ── Light theme override for Video Explorer ───────────────────────────
    st.markdown(
        """
        <style>
            .ve-filter-chip {
                display: inline-block;
                padding: 4px 14px;
                margin: 3px;
                border-radius: 20px;
                border: 1px solid #d0d0d0;
                background: #ffffff;
                color: #333333;
                font-size: 0.82rem;
                cursor: pointer;
                transition: all 0.15s;
            }
            .ve-filter-chip:hover { border-color: #ff6b6b; color: #ff6b6b; }
            .ve-filter-chip.active { background: #ff6b6b; color: #fff; border-color: #ff6b6b; }
            .ve-card {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
                padding: 16px;
                margin-bottom: 12px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06);
                transition: box-shadow 0.15s;
            }
            .ve-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.10); }
            .ve-thumb { border-radius: 8px; }
            .ve-title { font-size: 1rem; font-weight: 600; color: #1a1a2e; margin-bottom: 4px; }
            .ve-title a { color: #1a1a2e; text-decoration: none; }
            .ve-title a:hover { color: #ff6b6b; }
            .ve-meta { font-size: 0.82rem; color: #666; margin-bottom: 6px; }
            .ve-meta span { margin-right: 14px; }
            .ve-desc { font-size: 0.85rem; color: #555; line-height: 1.5; }
            .ve-stat-chip {
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 0.78rem;
                font-weight: 500;
                margin-right: 6px;
            }
            .ve-stat-views { background: #fff0f0; color: #d32f2f; }
            .ve-stat-likes { background: #f3e5f5; color: #7b1fa2; }
            .ve-stat-comments { background: #e3f2fd; color: #1565c0; }
            .ve-stat-ratio { background: #e8f5e9; color: #2e7d32; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🎥 Video Explorer")

    if not videos_df.empty:
        # ── Search ──────────────────────────────────────────────────────────
        search = st.text_input("🔍 Search videos", placeholder="Filter by title...", key="ve_search")

        filtered = videos_df.copy()
        if search:
            mask = filtered["title"].str.contains(search, case=False, na=False)
            filtered = filtered[mask]

        # ── Sort chips ──────────────────────────────────────────────────────
        st.caption("Sort by")
        sort_options = {
            "📅 Newest": ("published_at", False),
            "📅 Oldest": ("published_at", True),
            "👁 Most Views": ("views", False),
            "👁 Least Views": ("views", True),
            "👍 Most Likes": ("likes", False),
            "📊 Best Like/View": ("like_view_ratio", False),
        }
        sort_labels = list(sort_options.keys())
        sort_cols = st.columns(len(sort_labels))
        sort_key = st.session_state.get("ve_sort", sort_labels[0])

        for i, (label, col) in enumerate(zip(sort_labels, sort_cols)):
            is_active = sort_key == label
            if col.button(label, key=f"sort_{i}", type="primary" if is_active else "secondary"):
                sort_key = label
                st.session_state["ve_sort"] = sort_key

        sort_col, sort_asc = sort_options[sort_key]
        filtered = filtered.sort_values(
            sort_col, ascending=sort_asc, na_position="last"
        )

        # ── Quick filter chips ──────────────────────────────────────────────
        st.caption("Quick filters")
        chip_cols = st.columns(5)
        quick_filters = {
            "🔥 Top 10 by Views": lambda df: df.nlargest(10, "views"),
            "📈 Top 10 by Likes": lambda df: df.nlargest(10, "likes"),
            "💬 Top 10 by Comments": lambda df: df.nlargest(10, "comments"),
            "⭐ High Engagement": lambda df: df[df["like_view_ratio"] > df["like_view_ratio"].quantile(0.75)] if df["like_view_ratio"].notna().any() else df,
            "🔄 Show All": lambda df: df,
        }
        active_filter = st.session_state.get("ve_filter", "🔄 Show All")
        for i, (label, col) in enumerate(zip(quick_filters.keys(), chip_cols)):
            is_active = active_filter == label
            if col.button(label, key=f"filter_{i}", type="primary" if is_active else "secondary"):
                active_filter = label
                st.session_state["ve_filter"] = active_filter

        filtered = quick_filters[active_filter](filtered)

        st.caption(f"Showing {len(filtered)} video{'s' if len(filtered) != 1 else ''}")
        st.divider()

        # ── Horizontal video cards ──────────────────────────────────────────
        for _, row in filtered.iterrows():
            video = row.to_dict()
            vid = video.get("id", "")
            url = f"https://www.youtube.com/watch?v={vid}"
            thumb = video.get("thumbnail", "")
            title = video.get("title", "Untitled")
            views = video.get("views") or 0
            likes = video.get("likes")
            comments = video.get("comments")
            duration_s = video.get("duration_seconds", 0)
            published_at = video.get("published_at")
            desc = video.get("description", "")
            like_ratio = video.get("like_view_ratio")

            # Format duration
            dur_str = (
                f"{int(duration_s // 60)}:{int(duration_s % 60):02d}"
                if duration_s
                else "N/A"
            )
            # Format date
            pub_str = (
                published_at.strftime("%b %d, %Y")
                if pd.notna(published_at)
                else "N/A"
            )
            # Format ratio
            ratio_str = f"{like_ratio:.2%}" if pd.notna(like_ratio) else "N/A"

            col_thumb, col_meta = st.columns([1, 3])
            with col_thumb:
                if thumb:
                    st.markdown(
                        f'<a href="{url}" target="_blank">'
                        f'<img src="{thumb}" width="240" class="ve-thumb"></a>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="width:240px;height:135px;background:#f0f0f0;'
                        f'border-radius:8px;display:flex;align-items:center;'
                        f'justify-content:center;font-size:2rem;">🎬</div>',
                        unsafe_allow_html=True,
                    )
            with col_meta:
                st.markdown(
                    f'<div class="ve-title"><a href="{url}" target="_blank">{title}</a></div>',
                    unsafe_allow_html=True,
                )
                comments_display = f"{int(comments):,}" if pd.notna(comments) else "N/A"
                st.markdown(
                    f'<div class="ve-meta">'
                    f'<span>👁 {views:,} views</span>'
                    f'<span>👍 {f"{int(likes):,}" if pd.notna(likes) else "N/A"}</span>'
                    f'<span>💬 {comments_display}</span>'
                    f'<span>⏱ {dur_str}</span>'
                    f'<span>📅 {pub_str}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div>'
                    f'<span class="ve-stat-chip ve-stat-views">👁 {views:,}</span>'
                    f'<span class="ve-stat-chip ve-stat-likes">👍 {int(likes) if pd.notna(likes) else "N/A"}</span>'
                    f'<span class="ve-stat-chip ve-stat-comments">💬 {comments_display}</span>'
                    f'<span class="ve-stat-chip ve-stat-ratio">📊 {ratio_str}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if desc:
                    short_desc = desc[:200] + ("…" if len(desc) > 200 else "")
                    st.markdown(
                        f'<div class="ve-desc">{short_desc}</div>',
                        unsafe_allow_html=True,
                    )
            if vid:
                embed_video(vid, width=320, height=180)
            st.markdown("---")
    else:
        st.info("No videos found.")

elif view == "📈 Analytics":
    st.subheader("📈 Channel Analytics")

    if not videos_df.empty:
        # Views over time
        st.markdown("### 📅 Views Over Time")
        time_df = videos_df[["id", "published_at", "views", "title"]].sort_values("published_at").copy()
        time_df["published_at"] = time_df["published_at"].dt.strftime("%Y-%m-%d")

        import altair as alt

        line_chart = (
            alt.Chart(time_df)
            .mark_line(point=True, color="#ff6b6b")
            .encode(
                x=alt.X("published_at:T", title="Published Date"),
                y=alt.Y("views:Q", title="Views"),
                tooltip=[
                    alt.Tooltip("title:N", title="Video"),
                    alt.Tooltip("views:Q", title="Views", format=","),
                    alt.Tooltip("published_at:T", title="Date"),
                ],
                href="id:N",
            )
            .interactive()
            .properties(height=300)
        )
        st.altair_chart(line_chart, use_container_width=True)

        # Engagement distribution
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 👍 Like Distribution")
            like_data = videos_df[["title", "likes", "id"]].nlargest(15, "likes").copy()
            like_data["title_short"] = like_data["title"].str[:30]
            like_chart = (
                alt.Chart(like_data)
                .mark_bar(color="#ff6b6b")
                .encode(
                    x=alt.X("likes:Q", title="Likes"),
                    y=alt.Y("title_short:N", title="", sort="-x"),
                    tooltip=[
                        alt.Tooltip("title:N", title="Video"),
                        alt.Tooltip("likes:Q", title="Likes", format=","),
                    ],
                )
                .properties(height=400)
            )
            st.altair_chart(like_chart, use_container_width=True)
        with c2:
            st.markdown("### 💬 Comment Distribution")
            comment_data = videos_df[["title", "comments", "id"]].nlargest(15, "comments").copy()
            comment_data["title_short"] = comment_data["title"].str[:30]
            comment_chart = (
                alt.Chart(comment_data)
                .mark_bar(color="#e0aaff")
                .encode(
                    x=alt.X("comments:Q", title="Comments"),
                    y=alt.Y("title_short:N", title="", sort="-x"),
                    tooltip=[
                        alt.Tooltip("title:N", title="Video"),
                        alt.Tooltip("comments:Q", title="Comments", format=","),
                    ],
                )
                .properties(height=400)
            )
            st.altair_chart(comment_chart, use_container_width=True)

        # Summary stats
        st.markdown("### 📊 Summary Statistics")
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            metric_card("Total Views", f"{int(videos_df['views'].sum()):,}", video_id=top_video_id)
        with s2:
            metric_card("Total Likes", f"{int(videos_df['likes'].fillna(0).sum()):,}", video_id=top_video_id)
        with s3:
            metric_card("Total Comments", f"{int(videos_df['comments'].fillna(0).sum()):,}", video_id=top_video_id)
        with s4:
            metric_card("Avg Like/View", f"{videos_df['like_view_ratio'].mean():.2%}", video_id=top_video_id)
        with s5:
            metric_card("Avg Duration", f"{videos_df['duration_seconds'].mean() / 60:.1f} min", video_id=top_video_id)

        # Correlation table with embedded videos
        with st.expander("📋 Raw Data Table (with embedded videos)"):
            for _, row in videos_df.sort_values("published_at", ascending=False).iterrows():
                video = row.to_dict()
                video["duration_formatted"] = (
                    f"{int(video.get('duration_seconds', 0) // 60)}:{int(video.get('duration_seconds', 0) % 60):02d}"
                    if video.get("duration_seconds")
                    else "N/A"
                )
                video["published_formatted"] = (
                    row["published_at"].strftime("%b %d, %Y")
                    if pd.notna(row.get("published_at"))
                    else "N/A"
                )
                col_vid, col_meta = st.columns([1, 2])
                with col_vid:
                    embed_video(video["id"], width=240, height=135)
                with col_meta:
                    url = f"https://www.youtube.com/watch?v={video['id']}"
                    st.markdown(f"### [{video['title']}]({url})")
                    v_views = video.get("views") or 0
                    v_likes = video.get("likes") or 0
                    v_comments = video.get("comments") or 0
                    st.caption(
                        f"👁 {v_views:,} views | "
                        f"👍 {v_likes:,} | "
                        f"💬 {v_comments:,} | "
                        f"⏱ {video['duration_formatted']} | "
                        f"📅 {video['published_formatted']}"
                    )
                st.divider()
    else:
        st.info("No video data available for analytics.")

elif view == "🔐 Studio (Coming Soon)":
    st.subheader("🔐 YouTube Studio Analytics")
    st.warning("This view requires YouTube Studio OAuth credentials.")

    st.markdown(
        """
        ### What's coming:

        These metrics require **YouTube Analytics API** access with channel owner OAuth:

        - **Impressions & Click-Through Rate (CTR)** — How often your thumbnails get seen vs clicked
        - **Average View Duration** — How long viewers watch on average
        - **Audience Retention** — Where viewers drop off in your videos
        - **Traffic Sources** — Where your views come from (search, suggested, browse, etc.)
        - **Subscriber Growth Over Time** — Daily/weekly subscriber changes
        - **Revenue Estimates** — RPM, CPM (if monetized)

        ### How to enable:

        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Enable the **YouTube Analytics API** and **YouTube Reporting API**
        3. Create OAuth 2.0 credentials
        4. Add them to your `.env` file:

        ```
        YOUTUBE_CLIENT_ID=your-client-id
        YOUTUBE_CLIENT_SECRET=your-client-secret
        ```

        5. The first time you connect, you'll be prompted to authorize the app.

        *This feature is on the roadmap and will be implemented once OAuth credentials are provided.*
        """
    )

    # Show what we can already see
    st.divider()
    st.subheader("📊 What we can see right now (Public API)")
    if not videos_df.empty:
        st.success(
            f"Public API is working! We have data for {len(videos_df)} videos. "
            "Studio metrics will be added on top of this foundation."
        )
    else:
        st.info("Connect your API key to see public metrics.")

st.divider()
st.caption("🎬 YouTube Dashboard • Built with Streamlit by The Office • Data from YouTube Data API v3")
