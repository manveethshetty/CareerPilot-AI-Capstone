"""
CareerPilot AI — v3 dashboard UI layer.

PIPELINE (untouched):
  1. Parse PDF -> raw text
  2. Chunk text into sections (rag/chunker.py)
  3. Index chunks with hybrid BM25 + semantic retrieval (rag/retriever.py)
  4. Planner LLM decides which analysis tools to run (agent/planner.py)
  5. Executor runs the plan (agent/executor.py + agent/tools.py)
  6. Results rendered here + saved to history (utils/memory.py)

The pipeline visualization on the Dashboard shows REAL measured wall-
clock time per stage (time.perf_counter() around each actual step) —
not simulated pacing. KPI trend deltas are REAL comparisons against the
previous run's stored scores (utils/memory.py), not fabricated arrows.

8 sidebar pages are views over one shared session-state result — the
backend still only runs one Planner→Executor pass per Analyze click.
"""
import os
import json
import time
import streamlit as st
from dotenv import load_dotenv

from utils.pdf_parser import extract_text_from_pdf, basic_resume_stats
from rag.chunker import chunk_resume
from rag.retriever import HybridRetriever
from agent.planner import create_plan
from agent.executor import run_plan
from utils.memory import save_analysis, load_history, get_previous_scores
from utils.icons import icon
from utils.ui import (
    inject_css, render_sidebar_logo, render_sidebar_nav, render_sidebar_recent,
    render_hero, render_page_header, render_kpi_card, render_kpi_placeholder,
    render_skill_chips, render_project_card, render_ats_list, render_score_bar,
    render_priority_timeline, render_hbar, render_table, render_empty_state,
    render_pipeline, render_pdf_preview, PIPELINE_STAGES,
    TEAL, CYAN, WARNING, DANGER, TEXT_MUTED,
)
from utils.charts import skill_coverage_donut, ats_breakdown_bar

load_dotenv()
st.set_page_config(page_title="CareerPilot AI", page_icon="🧭", layout="wide")
inject_css()

# ── Session state defaults ───────────────────────────────────────────
_DEFAULTS = {
    "active_page": "dashboard",
    "results": None,
    "resume_stats": None,
    "resume_filename": None,
    "resume_bytes": None,
    "target_role": "",
    "previous_scores": None,
    "pipeline_timings": {},
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def skill_match_pct(current: list, missing: list) -> int:
    total = len(current) + len(missing)
    return round((len(current) / total) * 100) if total else 0


# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_logo()
    new_page = render_sidebar_nav(st.session_state.active_page)
    if new_page != st.session_state.active_page:
        st.session_state.active_page = new_page
        st.rerun()
    render_sidebar_recent(load_history())

page = st.session_state.active_page

# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════
if page == "dashboard":
    render_hero()

    if not os.environ.get("GROQ_API_KEY"):
        st.warning("GROQ_API_KEY is not set. Add it to a `.env` file locally, or to Streamlit Cloud → Settings → Secrets before deploying.")

    results = st.session_state.results
    overall = (results or {}).get("overall_recommendations", {})
    skills = (results or {}).get("skill_gap_analysis", {})
    match_pct = skill_match_pct(skills.get("current_skills", []), skills.get("missing_skills", []))
    prev = st.session_state.previous_scores

    k1, k2, k3, k4 = st.columns(4)
    if results:
        with k1:
            render_kpi_card("file-text", "Resume Score", int(overall.get("resume_score", 0)), prev.get("resume_score") if prev else None)
        with k2:
            render_kpi_card("search-check", "ATS Score", int(overall.get("ats_score", 0)), prev.get("ats_score") if prev else None)
        with k3:
            render_kpi_card("brain", "Skill Match", match_pct, prev.get("skill_match") if prev else None)
        with k4:
            render_kpi_card("compass", "Career Readiness", int(overall.get("career_readiness", 0)), prev.get("career_readiness") if prev else None)
    else:
        with k1:
            render_kpi_placeholder("file-text", "Resume Score")
        with k2:
            render_kpi_placeholder("search-check", "ATS Score")
        with k3:
            render_kpi_placeholder("brain", "Skill Match")
        with k4:
            render_kpi_placeholder("compass", "Career Readiness")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="cp-section-title">Resume Workspace</div>', unsafe_allow_html=True)
        target_role = st.text_input("Target role", value=st.session_state.target_role, placeholder="e.g. AI/ML Engineer, SDE-1")
        uploaded_file = st.file_uploader("Resume (PDF)", type=["pdf"], label_visibility="collapsed")
        c1, c2 = st.columns([1, 1])
        with c1:
            run_clicked = st.button("Analyze Resume", use_container_width=True, disabled=uploaded_file is None)
        with c2:
            st.markdown(f'<div style="padding-top:0.65rem;color:{TEXT_MUTED};font-size:0.82rem;">{icon("clock", 13, TEXT_MUTED)} Est. runtime: 20–40s</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cp-section-title">Pipeline</div>', unsafe_allow_html=True)
        pipeline_placeholder = st.empty()
        with pipeline_placeholder.container():
            done = len(PIPELINE_STAGES) if results else 0
            render_pipeline(done, st.session_state.pipeline_timings)

    if run_clicked and uploaded_file is not None:
        try:
            timings = {}
            t_start = time.perf_counter()

            with pipeline_placeholder.container():
                render_pipeline(0, {})
            resume_bytes = uploaded_file.getvalue()
            resume_text = extract_text_from_pdf(uploaded_file)
            stats = basic_resume_stats(resume_text)
            if stats["word_count"] < 30:
                st.error("Couldn't extract meaningful text from this PDF. Try a text-based (non-scanned) resume.")
                st.stop()
            timings[0] = time.perf_counter() - t_start  # PDF
            timings[1] = timings[0]  # Parser (same measured step as PDF read+extract)
            with pipeline_placeholder.container():
                render_pipeline(2, timings)

            t = time.perf_counter()
            chunks = chunk_resume(resume_text)
            timings[2] = time.perf_counter() - t  # Chunker
            with pipeline_placeholder.container():
                render_pipeline(3, timings)

            t = time.perf_counter()
            retriever = HybridRetriever()
            retriever.index(chunks)
            timings[3] = time.perf_counter() - t  # Hybrid Retrieval
            with pipeline_placeholder.container():
                render_pipeline(4, timings)

            t = time.perf_counter()
            plan_result = create_plan(resume_text[:800], target_role)
            timings[4] = time.perf_counter() - t  # Planner Agent
            with pipeline_placeholder.container():
                render_pipeline(5, timings)

            t = time.perf_counter()
            results = run_plan(plan_result["plan"], retriever, target_role)
            elapsed = time.perf_counter() - t
            # Executor Agent and LLM calls aren't separately measured — the
            # Executor loop IS the code that calls the LLM for each tool, so
            # there's no real sub-timing to split between them. Showing the
            # same true measured span on both is honest; inventing a 50/50
            # split would fabricate precision that doesn't exist.
            timings[5] = elapsed
            timings[6] = elapsed
            with pipeline_placeholder.container():
                render_pipeline(7, timings)

            t = time.perf_counter()
            st.session_state.previous_scores = get_previous_scores()
            save_analysis(uploaded_file.name, target_role, results)
            timings[7] = time.perf_counter() - t  # Career Report
            with pipeline_placeholder.container():
                render_pipeline(8, timings)

            st.session_state.results = results
            st.session_state.resume_stats = stats
            st.session_state.resume_filename = uploaded_file.name
            st.session_state.resume_bytes = resume_bytes
            st.session_state.target_role = target_role
            st.session_state.pipeline_timings = timings

            st.success(f"Analysis complete in {time.perf_counter() - t_start:.1f}s — see the sidebar pages for the full breakdown.")
            st.rerun()

        except EnvironmentError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    if not results:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        render_empty_state("Upload a resume and click Analyze to populate your dashboard.", "upload")

# ══════════════════════════════════════════════════════════════════
# RESUME ANALYSIS (split layout: PDF preview + summary)
# ══════════════════════════════════════════════════════════════════
elif page == "resume":
    render_page_header("Resume Analysis", "Executive summary alongside your original document", "file-text")
    results = st.session_state.results
    if not results:
        render_empty_state("Run an analysis from the Dashboard to see your resume breakdown.", "file-text")
    else:
        overall = results.get("overall_recommendations", {})
        stats = st.session_state.resume_stats or {}

        preview_col, summary_col = st.columns([2, 3])
        with preview_col:
            st.markdown('<div class="cp-section-title">Original Document</div>', unsafe_allow_html=True)
            if st.session_state.resume_bytes:
                render_pdf_preview(st.session_state.resume_bytes)
            else:
                render_empty_state("PDF preview unavailable for this session.", "file-text")

        with summary_col:
            st.markdown('<div class="cp-section-title">Executive Summary</div>', unsafe_allow_html=True)
            with st.expander("Summary", expanded=True):
                st.markdown(f"<div style='color:{TEXT_MUTED};font-size:0.9rem;line-height:1.6;'>{overall.get('overall_summary', 'N/A')}</div>", unsafe_allow_html=True)

            strengths = overall.get("strengths", [])
            if strengths:
                render_skill_chips("Strengths", strengths, "have", "sparkles")

            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            render_table(
                ["Metric", "Value"],
                [
                    ["Word count", str(stats.get("word_count", "—"))],
                    ["Email detected", "Yes" if stats.get("has_email") else "No"],
                    ["File", st.session_state.resume_filename or "—"],
                    ["Target role", st.session_state.target_role or "General"],
                ],
            )

# ══════════════════════════════════════════════════════════════════
# SKILL INTELLIGENCE
# ══════════════════════════════════════════════════════════════════
elif page == "skills":
    render_page_header("Skill Intelligence", "Current strengths vs. gaps for your target role", "brain")
    results = st.session_state.results
    if not results or not results.get("skill_gap_analysis"):
        render_empty_state("Run an analysis from the Dashboard to see your skill breakdown.", "brain")
    else:
        skills = results["skill_gap_analysis"]
        current = skills.get("current_skills", [])
        missing = skills.get("missing_skills", [])
        deepen = skills.get("skills_to_deepen", [])

        c1, c2 = st.columns([3, 2])
        with c1:
            render_skill_chips("Current Skills", current, "have", "check")
            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            render_skill_chips("Missing Skills", missing, "missing", "alert-triangle")
            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            render_skill_chips("Recommended to Deepen", deepen, "deepen", "target")
        with c2:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section-title">Skill Coverage</div>', unsafe_allow_html=True)
            st.plotly_chart(skill_coverage_donut(len(current), len(missing)), use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            render_hbar("Skills covered", len(current), len(current) + len(missing), TEAL)

# ══════════════════════════════════════════════════════════════════
# ATS OPTIMIZATION
# ══════════════════════════════════════════════════════════════════
elif page == "ats":
    render_page_header("ATS Optimization", "Applicant tracking system compatibility check", "search-check")
    results = st.session_state.results
    if not results or not results.get("ats_keyword_check"):
        render_empty_state("Run an analysis from the Dashboard to see your ATS check.", "search-check")
    else:
        ats = results["ats_keyword_check"]
        overall = results.get("overall_recommendations", {})
        missing_kw = ats.get("missing_keywords", [])
        flags = ats.get("formatting_flags", [])

        c1, c2 = st.columns([3, 2])
        with c1:
            render_ats_list("Missing Keywords", missing_kw, "warning")
            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            render_ats_list("Formatting Flags", flags, "danger")
        with c2:
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section-title">ATS Score</div>', unsafe_allow_html=True)
            render_score_bar("Overall ATS Score", int(overall.get("ats_score", 0)))
            render_score_bar("Keyword Coverage", int(ats.get("keyword_coverage", 0)))
            render_score_bar("Formatting Score", int(ats.get("formatting_score", 0)))
            render_score_bar("Readability", int(ats.get("readability_score", 0)))
            render_score_bar("Section Health", int(ats.get("section_health", 0)))
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
            st.markdown('<div class="cp-card">', unsafe_allow_html=True)
            st.markdown('<div class="cp-section-title">Issue Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(ats_breakdown_bar(len(missing_kw), len(flags)), use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PROJECT RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════
elif page == "projects":
    render_page_header("Project Recommendations", "New projects to strengthen your profile", "rocket")
    results = st.session_state.results
    if not results or not results.get("project_suggestions"):
        render_empty_state("Run an analysis from the Dashboard to see project ideas.", "rocket")
    else:
        projects = results["project_suggestions"].get("suggested_projects", [])
        if projects:
            for p in projects:
                render_project_card(p)
        else:
            render_empty_state("No project suggestions were generated for this plan.", "rocket")

# ══════════════════════════════════════════════════════════════════
# LEARNING ROADMAP (90-day windows mapped from the 3 priorities)
# ══════════════════════════════════════════════════════════════════
elif page == "roadmap":
    render_page_header("Learning Roadmap", "Prioritized next steps, paced across 90 days", "map")
    results = st.session_state.results
    if not results or not results.get("overall_recommendations"):
        render_empty_state("Run an analysis from the Dashboard to see your roadmap.", "map")
    else:
        priorities = results["overall_recommendations"].get("top_3_priorities", [])
        day_windows = ["Day 1–30", "Day 31–60", "Day 61–90"][:len(priorities)]
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        render_priority_timeline(priorities, day_windows)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Pacing is a suggested sequence based on priority order — not a scheduled project plan.")

# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════
elif page == "reports":
    render_page_header("Reports", "Export your analysis", "bar-chart")
    results = st.session_state.results
    if not results:
        render_empty_state("Run an analysis from the Dashboard to generate a report.", "bar-chart")
    else:
        overall = results.get("overall_recommendations", {})
        skills = results.get("skill_gap_analysis", {})
        render_table(
            ["Metric", "Score"],
            [
                ["Resume Score", f"{overall.get('resume_score', 0)}/100"],
                ["ATS Score", f"{overall.get('ats_score', 0)}/100"],
                ["Skill Match", f"{skill_match_pct(skills.get('current_skills', []), skills.get('missing_skills', []))}%"],
                ["Career Readiness", f"{overall.get('career_readiness', 0)}/100"],
            ],
        )
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        report_json = json.dumps(results, indent=2)
        st.download_button(
            "Download full report (JSON)",
            data=report_json,
            file_name=f"careerpilot_report_{st.session_state.resume_filename or 'resume'}.json",
            mime="application/json",
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
elif page == "settings":
    render_page_header("Settings", "Session and environment", "settings")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="cp-section-title">{icon("key", 15, TEXT_MUTED)} API Configuration</div>', unsafe_allow_html=True)
        key_status = "Configured" if os.environ.get("GROQ_API_KEY") else "Not set"
        status_color = TEAL if os.environ.get("GROQ_API_KEY") else DANGER
        st.markdown(f'<div style="color:{status_color};font-weight:600;font-size:0.9rem;">Groq API key: {key_status}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{TEXT_MUTED};font-size:0.82rem;margin-top:4px;">Set GROQ_API_KEY in your .env file or Streamlit Cloud secrets.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="cp-card">', unsafe_allow_html=True)
        st.markdown('<div class="cp-section-title">Session</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{TEXT_MUTED};font-size:0.85rem;">Current resume: {st.session_state.resume_filename or "None"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{TEXT_MUTED};font-size:0.85rem;">Target role: {st.session_state.target_role or "None"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Clear session", use_container_width=True):
            for k, v in _DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

    st.markdown("<div style='height:1.4rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="cp-section-title">Past Analyses</div>', unsafe_allow_html=True)
    history = load_history()
    if history:
        render_table(
            ["File", "Target Role", "Timestamp"],
            [[h["filename"], h["target_role"] or "General", h["timestamp"][:16]] for h in reversed(history[-10:])],
        )
    else:
        render_empty_state("No past analyses yet.", "clock")