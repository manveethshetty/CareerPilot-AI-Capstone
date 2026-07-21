"""
CareerPilot AI — UI component layer, v3: Apple / Stripe / Linear direction.

This module owns ONLY presentation. No RAG, agent, retrieval, or LLM
logic lives here. Functions here take already-computed data (tool
outputs, real measured timings, real trend deltas) and render it.

Design tokens:
  Background  #0B1220
  Card        #182235
  Border      #26314A  soft 1px, no glow
  Cyan        #0EA5E9  secondary / informational
  Teal        #14B8A6  primary / positive
  Orange      #F59E0B  warning
  Danger      #EF4444  errors only
  Text        #EDF1FA
  Text-muted  #8D96B8

Typography: Inter only, weight carries hierarchy (Linear/Stripe move).
No neon, no glassmorphism, no glow shadows. Borders + whitespace carry
structure instead of color intensity.
"""
import streamlit as st
import streamlit.components.v1 as components
from utils.icons import icon

# ── Design tokens ────────────────────────────────────────────────────
BG = "#0B1220"
CARD = "#182235"
CARD_RAISED = "#1E2A42"
BORDER = "#26314A"
CYAN = "#0EA5E9"
TEAL = "#14B8A6"
WARNING = "#F59E0B"
DANGER = "#EF4444"
TEXT = "#EDF1FA"
TEXT_MUTED = "#8D96B8"
TEXT_FAINT = "#5C6688"

NAV_ITEMS = [
    ("dashboard", "dashboard", "Dashboard"),
    ("resume", "file-text", "Resume Analysis"),
    ("skills", "brain", "Skill Intelligence"),
    ("ats", "search-check", "ATS Optimization"),
    ("projects", "rocket", "Project Recommendations"),
    ("roadmap", "map", "Learning Roadmap"),
    ("reports", "bar-chart", "Reports"),
    ("settings", "settings", "Settings"),
]

TECH_BADGES = ["Hybrid RAG", "Planner Agent", "Executor Agent", "Groq Llama 3.3", "ChromaDB", "Semantic Search"]

PIPELINE_STAGES = [
    ("PDF", "file-text"),
    ("Parser", "layers"),
    ("Chunker", "layers"),
    ("Hybrid Retrieval", "database"),
    ("Planner Agent", "git-branch"),
    ("Executor Agent", "cpu"),
    ("LLM (Groq)", "cpu"),
    ("Career Report", "file-check"),
]


def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {BG}; color: {TEXT}; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px; }}

    .cp-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.15rem 1.3rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
        transition: border-color 0.15s ease, transform 0.15s ease;
        animation: cpFade 0.35s ease-out;
    }}
    .cp-card:hover {{ border-color: #34405F; transform: translateY(-1px); }}
    .cp-card-tight {{ padding: 0.9rem 1.05rem; }}
    .cp-card-static:hover {{ transform: none; }}

    @keyframes cpFade {{ from {{ opacity:0; transform: translateY(4px);}} to {{ opacity:1; transform: translateY(0);}} }}

    section[data-testid="stSidebar"] {{ background: {CARD}; border-right: 1px solid {BORDER}; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.3rem; }}
    .cp-logo {{ display:flex; align-items:center; gap:10px; padding:0 0.2rem 1rem 0.2rem; margin-bottom:0.5rem; border-bottom:1px solid {BORDER}; }}
    .cp-logo-mark {{ width:28px; height:28px; border-radius:7px; background:{TEAL}; display:flex; align-items:center; justify-content:center; color:{BG}; flex-shrink:0; }}
    .cp-logo-text {{ font-weight:700; font-size:1.0rem; color:{TEXT}; letter-spacing:-0.01em; }}

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        background: transparent; border: 1px solid transparent; border-radius: 8px;
        color: {TEXT_MUTED}; font-weight: 500; font-size: 0.86rem;
        text-align: left; justify-content: flex-start; padding: 0.48rem 0.6rem;
        box-shadow: none; width: 100%;
        transition: background 0.15s ease, color 0.15s ease, padding-left 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background: {CARD_RAISED}; color: {TEXT}; padding-left: 0.8rem;
        transform: none; box-shadow: none;
    }}

    .main div[data-testid="stButton"] > button {{
        background: {TEAL}; color: #062821; border: none; border-radius: 10px;
        font-weight: 600; font-size: 0.9rem; padding: 0.55rem 1.05rem;
        box-shadow: none; transition: filter 0.12s ease;
    }}
    .main div[data-testid="stButton"] > button:hover {{ filter: brightness(1.08); transform: none; box-shadow: none; }}

    .stTextInput input {{ background: {CARD_RAISED}; border: 1px solid {BORDER}; border-radius: 9px; color: {TEXT}; }}
    .stTextInput input:focus {{ border-color: {TEAL}; box-shadow: 0 0 0 1px {TEAL}; }}

    div[data-testid="stFileUploaderDropzone"] {{ background: {CARD}; border: 1px dashed {BORDER}; border-radius: 14px; }}
    div[data-testid="stFileUploaderDropzone"]:hover {{ border-color: {CYAN}; }}

    .cp-hero-title {{ font-weight: 800; font-size: 1.9rem; color: {TEXT}; letter-spacing: -0.015em; margin: 0; }}
    .cp-hero-subtitle {{ font-size: 0.98rem; color: {TEXT_MUTED}; margin-top: 2px; margin-bottom: 0.75rem; }}
    .cp-badge-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1.4rem; }}
    .cp-tech-badge {{
        font-size: 0.72rem; font-weight: 600; color: {TEXT_MUTED};
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 999px;
        padding: 3px 11px;
    }}

    .cp-page-title {{ font-weight: 800; font-size: 1.55rem; color: {TEXT}; letter-spacing: -0.01em; margin-bottom: 2px; }}
    .cp-page-subtitle {{ font-size: 0.9rem; color: {TEXT_MUTED}; margin-bottom: 1.3rem; }}
    .cp-section-title {{ font-weight: 700; font-size: 0.95rem; color: {TEXT}; margin: 0 0 0.75rem 0; display:flex; align-items:center; gap:8px; }}
    .cp-eyebrow {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 0.07em; color: {TEXT_FAINT}; text-transform: uppercase; margin-bottom: 0.25rem; }}

    .cp-kpi-top {{ display:flex; justify-content:space-between; align-items:flex-start; }}
    .cp-kpi-icon {{ width:34px; height:34px; border-radius:9px; display:flex; align-items:center; justify-content:center; background: {CARD_RAISED}; }}
    .cp-kpi-trend {{ display:flex; align-items:center; gap:3px; font-size:0.76rem; font-weight:700; padding:2px 7px; border-radius:6px; }}
    .cp-kpi-value {{ font-size: 1.9rem; font-weight: 800; color: {TEXT}; line-height:1.1; margin-top:0.5rem; }}
    .cp-kpi-label {{ font-size: 0.8rem; color: {TEXT_MUTED}; font-weight:600; margin-top:2px; }}
    .cp-kpi-insight {{ font-size: 0.78rem; color: {TEXT_FAINT}; margin-top: 0.55rem; padding-top: 0.55rem; border-top: 1px solid {BORDER}; }}

    .cp-chip {{ display:inline-flex; align-items:center; padding:4px 11px; border-radius:7px; font-size:0.8rem; font-weight:600; margin:3px 6px 3px 0; border:1px solid {BORDER}; }}
    .cp-chip-have {{ background: rgba(20,184,166,0.09); color: {TEAL}; border-color: rgba(20,184,166,0.28); }}
    .cp-chip-missing {{ background: rgba(245,158,11,0.09); color: {WARNING}; border-color: rgba(245,158,11,0.28); }}
    .cp-chip-deepen {{ background: rgba(14,165,233,0.09); color: {CYAN}; border-color: rgba(14,165,233,0.28); }}
    .cp-chip-tech {{ background: {CARD_RAISED}; color: {CYAN}; border-color: {BORDER}; }}

    .cp-badge {{ display:inline-flex; align-items:center; gap:4px; padding:2px 9px; border-radius:6px; font-size:0.68rem; font-weight:700; letter-spacing:0.02em; text-transform:uppercase; border:1px solid {BORDER}; color:{TEXT_MUTED}; }}
    .cp-badge-warning {{ color:{WARNING}; border-color:rgba(245,158,11,0.3); background:rgba(245,158,11,0.06); }}
    .cp-badge-danger {{ color:{DANGER}; border-color:rgba(239,68,68,0.3); background:rgba(239,68,68,0.06); }}
    .cp-badge-teal {{ color:{TEAL}; border-color:rgba(20,184,166,0.3); background:rgba(20,184,166,0.06); }}

    .cp-hbar-track {{ width:100%; height:7px; border-radius:4px; background:{CARD_RAISED}; overflow:hidden; margin-top:5px; }}
    .cp-hbar-fill {{ height:100%; border-radius:4px; transition: width 0.6s ease; }}

    .cp-stage {{ display:flex; align-items:center; gap:10px; padding:8px 0; }}
    .cp-stage-icon {{ width:26px; height:26px; border-radius:7px; display:flex; align-items:center; justify-content:center; border:1.5px solid {BORDER}; flex-shrink:0; transition: all 0.2s ease; }}
    .cp-stage-icon-active {{ border-color:{TEAL}; background: rgba(20,184,166,0.1); }}
    .cp-stage-icon-done {{ background:{TEAL}; border-color:{TEAL}; }}
    .cp-stage-label {{ font-size:0.85rem; color:{TEXT_MUTED}; flex-grow:1; }}
    .cp-stage-label-done {{ color:{TEXT}; }}
    .cp-stage-timing {{ font-size:0.74rem; color:{TEXT_FAINT}; font-variant-numeric: tabular-nums; }}
    .cp-stage-connector {{ width:1.5px; height:10px; background:{BORDER}; margin-left:12.5px; }}

    .cp-timeline {{ position:relative; padding-left:26px; }}
    .cp-timeline::before {{ content:''; position:absolute; left:8px; top:4px; bottom:4px; width:1.5px; background:{BORDER}; }}
    .cp-timeline-item {{ position:relative; margin-bottom:1.15rem; }}
    .cp-timeline-dot {{ position:absolute; left:-26px; top:3px; width:15px; height:15px; border-radius:50%; background:{CARD}; border:2px solid {TEAL}; }}
    .cp-timeline-label {{ font-size:0.72rem; font-weight:700; color:{TEAL}; text-transform:uppercase; letter-spacing:0.05em; }}

    .cp-table {{ width:100%; border-collapse:collapse; font-size:0.87rem; }}
    .cp-table th {{ text-align:left; padding:8px 10px; color:{TEXT_FAINT}; font-weight:600; font-size:0.73rem; text-transform:uppercase; letter-spacing:0.04em; border-bottom:1px solid {BORDER}; }}
    .cp-table td {{ padding:9px 10px; border-bottom:1px solid {BORDER}; color:{TEXT}; }}
    .cp-table tr:last-child td {{ border-bottom:none; }}

    .cp-skeleton {{ background: linear-gradient(90deg, {CARD} 25%, {CARD_RAISED} 50%, {CARD} 75%); background-size: 200% 100%; animation: cpShimmer 1.4s infinite; border-radius: 8px; }}
    @keyframes cpShimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}

    /* ── Locked KPI placeholder (pre-analysis, eye-catching not shimmery) ── */
    .cp-kpi-locked {{
        border: 1.5px dashed {BORDER};
        background: linear-gradient(155deg, {CARD} 60%, rgba(20,184,166,0.04) 100%);
        position: relative; overflow: hidden;
    }}
    .cp-kpi-locked::after {{
        content: ''; position: absolute; top: -30%; right: -20%;
        width: 90px; height: 90px; border-radius: 50%;
        background: radial-gradient(circle, rgba(20,184,166,0.16) 0%, transparent 70%);
        animation: cpKpiGlow 3s ease-in-out infinite;
    }}
    @keyframes cpKpiGlow {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}
    .cp-kpi-icon-locked {{ background: {CARD_RAISED}; border: 1px dashed {BORDER}; }}
    .cp-kpi-pulse-dot {{
        width: 8px; height: 8px; border-radius: 50%; background: {TEAL};
        margin-top: 4px; animation: cpPulseDot 1.6s ease-in-out infinite;
    }}
    @keyframes cpPulseDot {{
        0%, 100% {{ opacity: 0.35; box-shadow: 0 0 0 0 rgba(20,184,166,0.4); }}
        50% {{ opacity: 1; box-shadow: 0 0 0 4px rgba(20,184,166,0); }}
    }}

    button[data-baseweb="tab"] {{ font-weight:600; color:{TEXT_MUTED}; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color:{TEAL} !important; }}
    div[data-baseweb="tab-highlight"] {{ background-color:{TEAL} !important; }}
    .streamlit-expanderHeader, div[data-testid="stExpander"] summary {{
        background:{CARD} !important; border:1px solid {BORDER} !important; border-radius:10px !important;
        color:{TEXT} !important; font-weight:600 !important; transition: border-color 0.15s ease;
    }}
    div[data-testid="stExpander"] {{ border:none !important; }}
    div[data-testid="stExpander"] summary:hover {{ border-color: {TEAL} !important; }}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_logo():
    st.markdown(f"""
    <div class="cp-logo">
        <div class="cp-logo-mark">{icon('compass', 16, "#062821")}</div>
        <div class="cp-logo-text">CareerPilot AI</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_nav(active_key: str) -> str:
    selected = active_key
    for key, icon_name, label in NAV_ITEMS:
        prefix = "● " if key == active_key else "○ "
        if st.button(f"{prefix}{label}", key=f"nav_{key}", use_container_width=True):
            selected = key
    return selected


def render_sidebar_recent(history: list):
    st.markdown(f'<div class="cp-eyebrow" style="margin-top:1rem;">Recent Resumes</div>', unsafe_allow_html=True)
    if not history:
        st.markdown(f'<div style="color:{TEXT_FAINT};font-size:0.8rem;">No resumes analyzed yet</div>', unsafe_allow_html=True)
        return
    for entry in reversed(history[-4:]):
        st.markdown(f"""
        <div style="padding:0.5rem 0.55rem;margin-bottom:0.35rem;border-radius:8px;background:{CARD_RAISED};">
            <div style="font-size:0.78rem;font-weight:600;color:{TEXT};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{entry['filename']}</div>
            <div style="font-size:0.7rem;color:{TEXT_FAINT};">{entry['target_role'] or 'general'} · {entry['timestamp'][5:16]}</div>
        </div>
        """, unsafe_allow_html=True)


def render_hero():
    badges_html = "".join(f'<span class="cp-tech-badge">{b}</span>' for b in TECH_BADGES)
    st.markdown(f"""
    <div class="cp-hero-title">{icon('dashboard', 22, TEAL)} &nbsp;CareerPilot AI</div>
    <div class="cp-hero-subtitle">AI Career Intelligence Platform</div>
    <div class="cp-badge-row">{badges_html}</div>
    """, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, icon_name: str = ""):
    icon_html = icon(icon_name, 20, TEAL) if icon_name else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:9px;">{icon_html}<div class="cp-page-title">{title}</div></div>
    <div class="cp-page-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def _score_color(score: int) -> str:
    if score >= 75:
        return TEAL
    if score >= 50:
        return WARNING
    return DANGER


def _insight_for(label: str, score: int) -> str:
    tier = "high" if score >= 75 else ("mid" if score >= 50 else "low")
    lines = {
        ("Resume Score", "high"): "Strong overall document",
        ("Resume Score", "mid"): "Solid, with room to sharpen",
        ("Resume Score", "low"): "Needs structural work",
        ("ATS Score", "high"): "Likely to clear ATS scans",
        ("ATS Score", "mid"): "Some keyword gaps remain",
        ("ATS Score", "low"): "High risk of ATS rejection",
        ("Skill Match", "high"): "Well aligned to target role",
        ("Skill Match", "mid"): "Partial alignment to role",
        ("Skill Match", "low"): "Significant skill gap",
        ("Career Readiness", "high"): "Ready to apply now",
        ("Career Readiness", "mid"): "A few gaps to close first",
        ("Career Readiness", "low"): "Early-stage for this role",
    }
    return lines.get((label, tier), "")


def render_kpi_card(icon_name: str, label: str, score: int, previous_score: int = None):
    color = _score_color(score)
    insight = _insight_for(label, score)

    if previous_score is None:
        trend_html = f'<span class="cp-kpi-trend" style="color:{TEXT_FAINT};background:{CARD_RAISED};">{icon("minus", 11, TEXT_FAINT)} first run</span>'
    else:
        delta = score - previous_score
        if delta > 0:
            trend_html = f'<span class="cp-kpi-trend" style="color:{TEAL};background:rgba(20,184,166,0.1);">{icon("trending-up", 11, TEAL)} +{delta}</span>'
        elif delta < 0:
            trend_html = f'<span class="cp-kpi-trend" style="color:{DANGER};background:rgba(239,68,68,0.1);">{icon("trending-down", 11, DANGER)} {delta}</span>'
        else:
            trend_html = f'<span class="cp-kpi-trend" style="color:{TEXT_MUTED};background:{CARD_RAISED};">{icon("minus", 11, TEXT_MUTED)} 0</span>'

    st.markdown(f"""
    <div class="cp-card">
        <div class="cp-kpi-top">
            <div class="cp-kpi-icon">{icon(icon_name, 17, color)}</div>
            {trend_html}
        </div>
        <div class="cp-kpi-value">{score}<span style="font-size:1rem;color:{TEXT_FAINT};">/100</span></div>
        <div class="cp-kpi-label">{label}</div>
        <div class="cp-kpi-insight">{insight}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_placeholder(icon_name: str, label: str):
    """Pre-analysis KPI state. Not a loading skeleton (nothing is being
    fetched yet) — a deliberate 'locked' card that previews the metric's
    icon and label with a pulsing accent, inviting the Analyze click."""
    st.markdown(f"""
    <div class="cp-card cp-card-static cp-kpi-locked">
        <div class="cp-kpi-top">
            <div class="cp-kpi-icon cp-kpi-icon-locked">{icon(icon_name, 17, TEXT_FAINT)}</div>
            <span class="cp-kpi-pulse-dot"></span>
        </div>
        <div class="cp-kpi-value" style="color:{TEXT_FAINT};">— <span style="font-size:1rem;">/100</span></div>
        <div class="cp-kpi-label">{label}</div>
        <div class="cp-kpi-insight" style="color:{TEXT_FAINT};">Run an analysis to unlock</div>
    </div>
    """, unsafe_allow_html=True)


def render_count_up(value: int, suffix: str = "", color: str = TEAL, size: str = "1.9rem"):
    components.html(f"""
    <div id="cp-counter" style="font-family:Inter,sans-serif;font-weight:800;font-size:{size};color:{color};">0{suffix}</div>
    <script>
    const el = document.getElementById('cp-counter');
    const target = {value};
    let current = 0;
    const duration = 700;
    const startTime = performance.now();
    function tick(now) {{
        const progress = Math.min((now - startTime) / duration, 1);
        current = Math.round(progress * target);
        el.textContent = current + "{suffix}";
        if (progress < 1) requestAnimationFrame(tick);
    }}
    requestAnimationFrame(tick);
    </script>
    """, height=int(float(size.replace("rem", "")) * 22))


def render_skill_chips(title: str, skills: list[str], variant: str, icon_name: str = ""):
    if not skills:
        chips_html = f'<span style="color:{TEXT_FAINT};font-size:0.85rem;">None identified</span>'
    else:
        chips_html = "".join(f'<span class="cp-chip cp-chip-{variant}">{s}</span>' for s in skills)
    icon_html = icon(icon_name, 15, TEXT_MUTED) if icon_name else ""
    st.markdown(f"""
    <div class="cp-card">
        <div class="cp-section-title">{icon_html} {title}</div>
        <div>{chips_html}</div>
    </div>
    """, unsafe_allow_html=True)


_DIFFICULTY_COLOR = {"Beginner": TEAL, "Intermediate": WARNING, "Advanced": DANGER}


def render_project_card(project: dict):
    tech = project.get("key_tech", [])
    tech_html = "".join(f'<span class="cp-chip cp-chip-tech">{t}</span>' for t in tech)
    difficulty = project.get("difficulty", "Intermediate")
    diff_color = _DIFFICULTY_COLOR.get(difficulty, CYAN)
    st.markdown(f"""
    <div class="cp-card" style="margin-bottom:0.85rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div class="cp-section-title" style="margin-bottom:0.5rem;">{icon('rocket', 16, TEAL)} {project.get('title', 'Untitled Project')}</div>
            <span class="cp-badge" style="color:{diff_color};border-color:{diff_color}44;background:{diff_color}18;">{difficulty}</span>
        </div>
        <div style="color:{TEXT_MUTED};font-size:0.89rem;line-height:1.55;margin-bottom:0.7rem;">{project.get('why', '')}</div>
        <div class="cp-eyebrow">Tech stack</div>
        <div style="margin-bottom:0.6rem;">{tech_html}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:0.6rem;padding-top:0.6rem;border-top:1px solid {BORDER};">
            <div><div class="cp-eyebrow">Resume Impact</div><div style="font-size:0.82rem;color:{TEXT};">{project.get('resume_impact', '—')}</div></div>
            <div><div class="cp-eyebrow">Learning Outcome</div><div style="font-size:0.82rem;color:{TEXT};">{project.get('learning_outcome', '—')}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_ats_list(title: str, items: list[str], severity: str):
    badge_class = "cp-badge-warning" if severity == "warning" else "cp-badge-danger"
    badge_text = "Keyword" if severity == "warning" else "Format"
    if not items:
        rows = f'<div style="color:{TEXT_FAINT};font-size:0.85rem;padding:6px 0;">No issues found</div>'
    else:
        rows = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.62rem 0;border-bottom:1px solid {BORDER};">'
            f'<span style="color:{TEXT};font-size:0.87rem;">{i}</span>'
            f'<span class="cp-badge {badge_class}">{badge_text}</span></div>'
            for i in items
        )
    st.markdown(f'<div class="cp-card"><div class="cp-section-title">{title}</div>{rows}</div>', unsafe_allow_html=True)


def render_score_bar(label: str, score: int):
    color = _score_color(score)
    st.markdown(f"""
    <div style="margin-bottom:0.85rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.84rem;color:{TEXT_MUTED};">
            <span>{label}</span><span style="color:{TEXT};font-weight:700;">{score}/100</span>
        </div>
        <div class="cp-hbar-track"><div class="cp-hbar-fill" style="width:{score}%;background:{color};"></div></div>
    </div>
    """, unsafe_allow_html=True)


def render_hbar(label: str, value: int, total: int, color: str = TEAL):
    pct = round((value / total) * 100) if total else 0
    st.markdown(f"""
    <div style="margin-bottom:0.85rem;">
        <div style="display:flex;justify-content:space-between;font-size:0.84rem;color:{TEXT_MUTED};">
            <span>{label}</span><span style="color:{TEXT};font-weight:700;">{value}/{total}</span>
        </div>
        <div class="cp-hbar-track"><div class="cp-hbar-fill" style="width:{pct}%;background:{color};"></div></div>
    </div>
    """, unsafe_allow_html=True)


def render_pipeline(active_index: int, timings: dict):
    """active_index: how many stages are complete (0..len(PIPELINE_STAGES)).
    timings: dict of stage_index -> seconds (float), only for completed stages."""
    rows = ""
    for i, (label, icon_name) in enumerate(PIPELINE_STAGES):
        is_done = i < active_index
        is_active = i == active_index
        icon_class = "cp-stage-icon-done" if is_done else ("cp-stage-icon-active" if is_active else "")
        icon_html = icon("check", 12, "#062821") if is_done else icon(icon_name, 12, TEAL if is_active else TEXT_FAINT)
        label_class = "cp-stage-label-done" if is_done else ""
        timing_html = f'<span class="cp-stage-timing">{timings[i]:.2f}s</span>' if i in timings else ""
        rows += f'<div class="cp-stage"><div class="cp-stage-icon {icon_class}">{icon_html}</div><div class="cp-stage-label {label_class}">{label}</div>{timing_html}</div>'
        if i < len(PIPELINE_STAGES) - 1:
            rows += '<div class="cp-stage-connector"></div>'
    st.markdown(f'<div class="cp-card cp-card-tight cp-card-static">{rows}</div>', unsafe_allow_html=True)


def render_priority_timeline(priorities: list[str], day_windows: list[str] = None):
    if not priorities:
        st.markdown(f'<div style="color:{TEXT_FAINT};">No priorities identified.</div>', unsafe_allow_html=True)
        return
    windows = day_windows or [f"Step {i+1}" for i in range(len(priorities))]
    items_html = "".join(
        f'<div class="cp-timeline-item"><div class="cp-timeline-dot"></div>'
        f'<div class="cp-timeline-label">{windows[i]}</div>'
        f'<div style="color:{TEXT};font-size:0.9rem;margin-top:2px;">{p}</div></div>'
        for i, p in enumerate(priorities)
    )
    st.markdown(f'<div class="cp-timeline">{items_html}</div>', unsafe_allow_html=True)


def render_table(headers: list[str], rows: list[list[str]]):
    head_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    st.markdown(f'<div class="cp-card"><table class="cp-table"><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table></div>', unsafe_allow_html=True)


def render_empty_state(message: str, icon_name: str = "sparkles"):
    st.markdown(f"""
    <div class="cp-card cp-card-static" style="text-align:center;padding:2.6rem 1.5rem;">
        <div style="opacity:0.5;margin-bottom:0.7rem;display:flex;justify-content:center;">{icon(icon_name, 30, TEXT_FAINT)}</div>
        <div style="color:{TEXT_MUTED};font-size:0.9rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def render_pdf_preview(pdf_bytes: bytes, max_pages: int = 3):
    """Renders PDF pages as images via pdfplumber (pure-Python, no system
    dependencies like Poppler/ImageMagick needed — works on Streamlit
    Cloud as-is). Replaces an earlier data-URI iframe approach that
    browsers like Edge block by default for security reasons."""
    import io
    import pdfplumber

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)
            pages_to_show = min(page_count, max_pages)
            st.markdown('<div class="cp-card cp-card-static" style="padding:0.6rem;">', unsafe_allow_html=True)
            for i in range(pages_to_show):
                img = pdf.pages[i].to_image(resolution=150)
                st.image(img.original, use_container_width=True)
                if i < pages_to_show - 1:
                    st.markdown(f'<div style="height:1px;background:{BORDER};margin:0.6rem 0;"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if page_count > max_pages:
                st.caption(f"Showing {max_pages} of {page_count} pages.")
    except Exception as e:
        st.markdown(f'<div class="cp-card cp-card-static" style="text-align:center;padding:2rem;color:{TEXT_MUTED};">Preview unavailable for this file.</div>', unsafe_allow_html=True)
        with st.expander("Why?"):
            st.caption(f"{type(e).__name__}: {e}")