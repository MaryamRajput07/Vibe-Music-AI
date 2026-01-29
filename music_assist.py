import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import streamlit as st
import streamlit.components.v1 as components

try:
    from textblob import TextBlob

    _TEXTBLOB_AVAILABLE = True
except Exception:
    TextBlob = None  # type: ignore
    _TEXTBLOB_AVAILABLE = False


APP_NAME = "VibeMusic AI"

# --- Spotify "database" (playlist IDs) ---
# Note: these are public Spotify playlist IDs (embeddable).
PLAYLISTS: Dict[str, Dict[str, object]] = {
    "lofi": {
        "name": "Lo-fi",
        "subtitle": "Late-night glow, soft beats, zero pressure.",
        "playlist_id": "37i9dQZF1DX8Uebhn9wzrS",  # Lo-Fi Beats
        "tags": ["lofi", "chill", "study", "beats", "relax", "ambient"],
    },
    "bollywood": {
        "name": "Bollywood",
        "subtitle": "Big feelings, bigger hooks, cinematic energy.",
        "playlist_id": "37i9dQZF1DX0XUfTFmNBRM",  # Bollywood Butter
        "tags": ["bollywood", "hindi", "india", "romance", "party", "hits"],
    },
    "pop": {
        "name": "Pop",
        "subtitle": "Bright, modern, and instantly addictive.",
        "playlist_id": "37i9dQZF1DXcBWIGoYBM5M",  # Today's Top Hits
        "tags": ["pop", "top hits", "chart", "dance", "viral", "energy"],
    },
    "focus": {
        "name": "Focus",
        "subtitle": "Deep work mode: locked in, calm, consistent.",
        "playlist_id": "37i9dQZF1DWZeKCadgRdKQ",  # Deep Focus
        "tags": ["focus", "deep work", "study", "concentration", "instrumental"],
    },
    "sad_aesthetic": {
        "name": "Sad Aesthetic",
        "subtitle": "Beautifully bittersweet—lean into the feeling.",
        "playlist_id": "37i9dQZF1DX7qK8ma5wgG1",  # Sad Songs
        "tags": ["sad", "aesthetic", "melancholy", "heartbreak", "moody"],
    },
}

HOME_ORDER: List[str] = ["lofi", "bollywood", "pop", "focus", "sad_aesthetic"]
PLAYLIST_ID_TO_KEY: Dict[str, str] = {
    str(v["playlist_id"]): k for k, v in PLAYLISTS.items() if "playlist_id" in v
}

VIBE_QUOTES: List[str] = [
    "Some nights the city hums in minor keys, and you finally understand yourself.",
    "Let the music do what words can’t: hold your heart without asking questions.",
    "You’re not behind—your bloom is just choosing a deeper season.",
    "Softness is not weakness. It’s a different kind of power.",
    "If you can feel it, you can survive it—one song at a time.",
    "Today, choose the playlist that forgives you for being human.",
    "Your mind is a sky. Let the sounds become weather, not a storm.",
    "Breathe in the silence between notes. That’s where healing hides.",
    "Even the saddest song is proof you’re still listening.",
    "Stay. The next track might be the one that returns you to yourself.",
    "Some songs don’t end — they become a room you revisit when you need to feel understood.",
    "If the world feels loud, choose a track that makes your thoughts gentle again.",
    "You don’t need to be okay to press play. You just need to keep listening.",
    "Let the bass carry the weight. Let the melody hold the hope.",
    "Tonight, don’t fix your feelings — soundtrack them.",
]


def _rotate_vibe_quote() -> None:
    current = st.session_state.get("vibe_quote")
    choices = [q for q in VIBE_QUOTES if q != current] or VIBE_QUOTES
    st.session_state.vibe_quote = random.choice(choices)


def _youtube_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def _link_button(label: str, url: str) -> None:
    # Streamlit has st.link_button in newer versions; provide a safe fallback.
    link_btn = getattr(st, "link_button", None)
    if callable(link_btn):
        link_btn(label, url, use_container_width=True)
        return
    st.markdown(f"[{label}]({url})")


def _inject_css() -> None:
    st.markdown(
        """
<style>
/* ====== VibeMusic AI — Premium UI Skin ====== */

/* Animated gradient background */
html, body, .stApp {
  height: 100%;
}

.stApp {
  background: linear-gradient(120deg, #05000a, #1a0636, #2a0b57, #05000a, #000000);
  background-size: 420% 420%;
  animation: vibeGradient 15s ease-in-out infinite;
}

@keyframes vibeGradient {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Typography & layout polish */
.block-container {
  padding-top: 2.0rem;
  padding-bottom: 6.5rem; /* room for now-playing bar */
  max-width: 1200px;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Sidebar glass */
div[data-testid="stSidebar"] > div {
  background: rgba(10, 6, 20, 0.45);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 255, 255, 0.10);
}

/* Global glass container utility */
.glass {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-radius: 18px;
}

/* Hero */
.vm-hero {
  padding: 18px 18px;
  margin-bottom: 18px;
}
.vm-title {
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: 0.2px;
  margin: 0;
  line-height: 1.15;
}
.vm-subtitle {
  margin-top: 8px;
  opacity: 0.86;
  font-size: 1.02rem;
}
.vm-badge {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 0.9rem;
  opacity: 0.92;
}
.vm-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #9b5cff, #3b1bff);
  box-shadow: 0 0 14px rgba(155, 92, 255, 0.65);
}

/* Genre cards */
.genre-card {
  padding: 16px 16px;
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}
.genre-card:hover {
  transform: scale(1.02);
  border-color: rgba(155, 92, 255, 0.35);
  box-shadow: 0 22px 70px rgba(0,0,0,0.45);
}
.genre-title {
  font-weight: 800;
  font-size: 1.18rem;
  margin: 0;
}
.genre-subtitle {
  margin-top: 8px;
  opacity: 0.85;
  font-size: 0.95rem;
  line-height: 1.35;
}

/* Buttons micro-interactions */
div.stButton > button {
  border-radius: 14px !important;
  border: 1px solid rgba(255, 255, 255, 0.16) !important;
  background: rgba(255,255,255,0.10) !important;
  color: rgba(255,255,255,0.92) !important;
  transition: transform 160ms ease, background 160ms ease, border-color 160ms ease;
}
div.stButton > button:hover {
  transform: scale(1.05);
  background: rgba(155, 92, 255, 0.16) !important;
  border-color: rgba(155, 92, 255, 0.32) !important;
}

/* Inputs as glass */
div[data-baseweb="textarea"] textarea,
div[data-baseweb="input"] input {
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: rgba(255,255,255,0.92) !important;
  border-radius: 14px !important;
}

/* Spotify player */
iframe {
  border-radius: 18px !important;
  box-shadow: 0 22px 70px rgba(0,0,0,0.55);
}
.player-shell {
  padding: 14px 14px;
}

/* Now Playing bar */
.now-playing {
  position: fixed;
  left: 18px;
  right: 18px;
  bottom: 14px;
  z-index: 9999;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.np-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.np-pulse {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #9b5cff;
  box-shadow: 0 0 18px rgba(155, 92, 255, 0.85);
  animation: npPulse 1.8s ease-in-out infinite;
}
@keyframes npPulse {
  0%, 100% { transform: scale(0.85); opacity: 0.75; }
  50% { transform: scale(1.15); opacity: 1.0; }
}
.np-title {
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.np-meta {
  opacity: 0.86;
  font-size: 0.9rem;
  white-space: nowrap;
}

/* Make radio look cleaner */
div[role="radiogroup"] label {
  padding: 6px 8px;
  border-radius: 12px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _init_state() -> None:
    if "current_playlist_key" not in st.session_state:
        st.session_state.current_playlist_key = "lofi"
    if "current_playlist_reason" not in st.session_state:
        st.session_state.current_playlist_reason = "Default"
    if "current_p" not in st.session_state:
        st.session_state.current_p = str(PLAYLISTS[st.session_state.current_playlist_key]["playlist_id"])
    if "last_mood_analysis" not in st.session_state:
        st.session_state.last_mood_analysis = None
    if "vibe_quote" not in st.session_state:
        st.session_state.vibe_quote = random.choice(VIBE_QUOTES)
    if "_last_nav" not in st.session_state:
        st.session_state._last_nav = None


def _set_current_playlist(key: str, reason: str) -> None:
    if key not in PLAYLISTS:
        return
    st.session_state.current_playlist_key = key
    st.session_state.current_playlist_reason = reason
    st.session_state.current_p = str(PLAYLISTS[key]["playlist_id"])
    st.session_state.current_playlist_name = str(PLAYLISTS[key]["name"])


def _current_playlist() -> Dict[str, object]:
    key = st.session_state.get("current_playlist_key")
    if isinstance(key, str) and key in PLAYLISTS:
        return PLAYLISTS[key]

    playlist_id = st.session_state.get("current_p")
    if isinstance(playlist_id, str) and playlist_id in PLAYLIST_ID_TO_KEY:
        inferred_key = PLAYLIST_ID_TO_KEY[playlist_id]
        st.session_state.current_playlist_key = inferred_key
        return PLAYLISTS[inferred_key]

    st.session_state.current_playlist_key = "lofi"
    st.session_state.current_p = str(PLAYLISTS["lofi"]["playlist_id"])
    return PLAYLISTS["lofi"]


def _spotify_embed_url(playlist_id: str) -> str:
    # Spotify embed (playlist)
    # Note: Browsers may block autoplay; we still request it for instant-start where allowed.
    return (
        f"https://open.spotify.com/embed/playlist/{playlist_id}"
        f"?utm_source=generator&theme=0&autoplay=1"
    )


def _render_hero() -> None:
    st.markdown(
        f"""
<div class="vm-hero glass">
  <div class="vm-title">{APP_NAME}</div>
  <div class="vm-subtitle">A premium AI-powered music space — glassy visuals, mood intelligence, and playlists that match your moment.</div>
  <div class="vm-badge"><span class="vm-dot"></span> Live vibe engine • Spotify embed • Session-safe “Now Playing”</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_player() -> None:
    pl = _current_playlist()
    playlist_id = str(pl["playlist_id"])
    playlist_name = str(pl["name"])
    src = _spotify_embed_url(playlist_id)

    left, mid, right = st.columns([1, 5, 1], vertical_alignment="center")
    with mid:
        st.markdown('<div class="player-shell glass">', unsafe_allow_html=True)
        components.iframe(src, width=900, height=420, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption(f"Showing: {playlist_name}")


def _render_genre_grid(keys: List[str], *, key_prefix: str) -> None:
    rows = [keys[i : i + 3] for i in range(0, len(keys), 3)]
    for row_idx, row in enumerate(rows):
        cols = st.columns(3, gap="large")
        for col_idx in range(3):
            with cols[col_idx]:
                if col_idx >= len(row):
                    st.write("")
                    continue
                k = row[col_idx]
                pl = PLAYLISTS[k]
                st.markdown(
                    f"""
<div class="genre-card glass">
  <div class="genre-title">{pl["name"]}</div>
  <div class="genre-subtitle">{pl["subtitle"]}</div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Play",
                    key=f"{key_prefix}_play_{row_idx}_{col_idx}_{k}",
                    use_container_width=True,
                ):
                    _set_current_playlist(k, reason="Manual selection")


def _mood_to_playlist(polarity: float, subjectivity: float) -> Tuple[str, str]:
    """
    Maps TextBlob sentiment to a playlist key.
    Returns: (playlist_key, explanation)
    """
    # More positive -> Pop, moderately positive & expressive -> Bollywood
    if polarity >= 0.35:
        return "pop", "High positive energy detected → Pop."
    if polarity >= 0.10 and subjectivity >= 0.45:
        return "bollywood", "Warm positive + expressive tone → Bollywood."
    # Neutral: choose Focus vs Lo-fi based on subjectivity (objective = focus)
    if -0.10 < polarity < 0.10:
        if subjectivity < 0.40:
            return "focus", "Neutral + objective tone → Focus."
        return "lofi", "Neutral + reflective tone → Lo-fi."
    # Negative: sad aesthetic vs lo-fi
    if polarity <= -0.35:
        return "sad_aesthetic", "Strong negative sentiment → Sad Aesthetic."
    return "lofi", "Mildly negative / mellow tone → Lo-fi."


def _render_home() -> None:
    st.subheader("Home Dashboard")
    st.write("Pick a genre — the player updates instantly and stays consistent across pages.")
    _render_genre_grid(HOME_ORDER, key_prefix="home")


def _render_smart_search() -> None:
    st.subheader("Smart Search")
    query = st.text_input(
        "Search by vibe, genre, or keyword",
        placeholder="Try: chill, study, heartbreak, hindi, energy…",
    )

    if not query.strip():
        st.write("Type something to discover playlists.")
        _render_genre_grid(HOME_ORDER, key_prefix="search_default")
        return

    q = query.strip().lower()
    results: List[str] = []
    for k, pl in PLAYLISTS.items():
        hay = " ".join(
            [
                str(pl.get("name", "")),
                str(pl.get("subtitle", "")),
                " ".join([str(t) for t in (pl.get("tags", []) or [])]),
            ]
        ).lower()
        if q in hay:
            results.append(k)

    if not results:
        st.info("No local matches found in your playlist database.")
        st.write("Want to explore anyway? Search it instantly on YouTube:")
        _link_button("Search on YouTube", _youtube_search_url(query.strip()))
        return

    st.write(f"Results: {len(results)}")
    _render_genre_grid(results, key_prefix="search")


def _render_mood_scanner() -> None:
    st.subheader("AI Mood Scanner")
    st.write("Tell me how you feel. I’ll analyze the vibe and match a playlist.")

    if not _TEXTBLOB_AVAILABLE:
        st.error(
            "TextBlob is not installed. Install it first: `pip install textblob` (and optionally `python -m textblob.download_corpora`)."
        )
        st.stop()

    text = st.text_area(
        "Your mood (1–3 sentences is perfect)",
        placeholder="Example: I feel calm but a little overwhelmed, like I need quiet focus.",
        height=140,
        key="mood_input",
    )

    cols = st.columns([1, 1, 2])
    with cols[0]:
        analyze = st.button("Scan Mood", use_container_width=True)
    with cols[1]:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        st.session_state.last_mood_analysis = None
        st.session_state.mood_input = ""
        st.rerun()

    if analyze:
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            st.warning("Write something first, then scan.")
            return

        blob = TextBlob(cleaned)
        polarity = float(blob.sentiment.polarity)
        subjectivity = float(blob.sentiment.subjectivity)
        picked_key, why = _mood_to_playlist(polarity, subjectivity)

        st.session_state.last_mood_analysis = {
            "text": cleaned,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "picked_key": picked_key,
            "why": why,
        }
        _set_current_playlist(picked_key, reason="AI Mood Scanner")
        _rotate_vibe_quote()
        # Re-run so the embedded player refreshes immediately with the new playlist.
        st.rerun()

    analysis = st.session_state.get("last_mood_analysis")
    if analysis:
        pl = PLAYLISTS[str(analysis["picked_key"])]
        st.markdown(
            f"""
<div class="glass" style="padding: 14px 16px; margin-top: 10px;">
  <div style="font-weight:800; font-size:1.05rem; margin-bottom:8px;">Mood Result</div>
  <div style="opacity:0.92; margin-bottom:10px;">{analysis["why"]}</div>
  <div style="opacity:0.86; font-size:0.95rem;">
    Polarity: <b>{analysis["polarity"]:+.2f}</b> • Subjectivity: <b>{analysis["subjectivity"]:.2f}</b>
  </div>
  <div style="margin-top:10px; font-weight:800;">Matched Playlist: {pl["name"]}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No scan yet — the player stays on the default Lo-fi playlist until you scan.")


def _render_now_playing() -> None:
    pl = _current_playlist()
    name = str(pl["name"])
    reason = str(st.session_state.get("current_playlist_reason", ""))
    st.markdown(
        f"""
<div class="now-playing glass">
  <div class="np-left">
    <div class="np-pulse"></div>
    <div class="np-title">Now Playing: {name}</div>
  </div>
  <div class="np-meta">{reason}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> str:
    with st.sidebar:
        st.markdown(f"### {APP_NAME}")
        st.caption("Premium glass UI • AI mood mapping • Spotify embed")

        nav = st.radio(
            "Navigate",
            ["Home", "Smart Search", "AI Mood Scanner"],
            index=0,
        )
        if nav != st.session_state.get("_last_nav"):
            st.session_state._last_nav = nav
            _rotate_vibe_quote()

        st.markdown("---")
        if st.button("AI Vibe Poetry", use_container_width=True):
            _rotate_vibe_quote()

        st.markdown(
            f"""
<div class="glass" style="padding: 12px 12px; margin-top: 10px;">
  <div style="font-weight:800; margin-bottom:6px;">Vibe Quote</div>
  <div style="opacity:0.92; line-height:1.35;">{st.session_state.vibe_quote}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        cur = _current_playlist()
        st.caption(f"Selected: **{cur['name']}**")

    return nav


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _inject_css()
    _init_state()

    nav = _render_sidebar()

    _render_hero()
    player_slot = st.empty()

    if nav == "Home":
        _render_home()
    elif nav == "Smart Search":
        _render_smart_search()
    else:
        _render_mood_scanner()

    with player_slot.container():
        _render_player()

    _render_now_playing()


if __name__ == "__main__":
    main()

