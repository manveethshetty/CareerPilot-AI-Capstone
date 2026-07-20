"""
Each tool: (1) builds a targeted retrieval query, (2) pulls the most
relevant resume chunks via the hybrid retriever, (3) calls the LLM with a
tool-specific prompt grounded in only that retrieved context. This keeps
each call focused and avoids stuffing the entire resume into every prompt.
"""
from agent.llm_client import call_llm_json


def tool_skill_gap_analysis(retriever, target_role: str) -> dict:
    query = f"technical skills, programming languages, tools, frameworks used {target_role}"
    context_chunks = retriever.retrieve(query, top_k=6)
    context = "\n---\n".join(c["text"] for c in context_chunks)

    system_prompt = """You are a technical resume reviewer. Based ONLY on the
provided resume excerpts, identify skill gaps relative to the target role.
Return STRICT JSON: {"current_skills": [...], "missing_skills": [...],
"skills_to_deepen": [...]}. Keep each list to 4-8 concise items."""
    user_prompt = f"Target role: {target_role or 'General software/AI engineering role'}\n\nResume excerpts:\n{context}"
    return call_llm_json(system_prompt, user_prompt)


def tool_project_suggestions(retriever, target_role: str) -> dict:
    query = f"projects built, technologies used in projects {target_role}"
    context_chunks = retriever.retrieve(query, top_k=6)
    context = "\n---\n".join(c["text"] for c in context_chunks)

    system_prompt = """You are a career mentor. Based ONLY on the provided
resume excerpts, suggest NEW projects the candidate should build to
strengthen their resume for the target role. Favor projects that fill
gaps not already covered. For each project also give a difficulty level,
the concrete resume impact, and the learning outcome. Return STRICT JSON:
{"suggested_projects": [{"title": "...", "why": "...", "key_tech": ["..."],
"difficulty": "Beginner|Intermediate|Advanced", "resume_impact": "one
sentence on what this proves to a recruiter", "learning_outcome": "one
sentence on the concrete skill gained"}]}.
Suggest 3-4 projects."""
    user_prompt = f"Target role: {target_role or 'General software/AI engineering role'}\n\nResume excerpts:\n{context}"
    return call_llm_json(system_prompt, user_prompt)


def tool_ats_keyword_check(retriever, target_role: str) -> dict:
    query = f"job title, role keywords, industry terms {target_role}"
    context_chunks = retriever.retrieve(query, top_k=6)
    context = "\n---\n".join(c["text"] for c in context_chunks)

    system_prompt = """You are an ATS (Applicant Tracking System) optimization
expert. Based ONLY on the provided resume excerpts, identify likely ATS
keyword gaps for the target role and formatting risks (e.g. missing
section headers, non-standard bullet structure). Also give four 0-100
sub-scores reflecting your honest judgment: keyword_coverage (how well
the resume's language matches expected role keywords), formatting_score
(how cleanly it would parse in an ATS), readability_score (clarity and
scannability for a human reviewer), section_health (whether standard
sections like Skills/Experience/Education are present and well-formed).
Return STRICT JSON: {"missing_keywords": [...], "formatting_flags": [...],
"keyword_coverage": 0-100, "formatting_score": 0-100,
"readability_score": 0-100, "section_health": 0-100}."""
    user_prompt = f"Target role: {target_role or 'General software/AI engineering role'}\n\nResume excerpts:\n{context}"
    return call_llm_json(system_prompt, user_prompt)


def tool_overall_recommendations(retriever, target_role: str, prior_results: dict) -> dict:
    """Synthesizer: combines outputs of earlier tools into a final summary,
    including three grounded 0-100 scores used by the dashboard metric
    cards. Scores are the LLM's judgment based on the actual analysis
    that already ran (skill gaps, project suggestions, ATS check) —
    not fabricated in the UI layer."""
    full_context = retriever.get_all_text()[:3000]  # cap context length

    system_prompt = """You are a senior technical recruiter giving final,
actionable feedback. You are given the full resume text AND the outputs
of earlier analysis tools (skill gaps, project suggestions, ATS check).
Synthesize everything into a concise, prioritized action plan, plus three
scores from 0-100 that reflect your honest judgment based on the resume
and the prior tool outputs (not arbitrary numbers):
- resume_score: overall strength of the resume as a document
- ats_score: how well it would survive an ATS keyword/format scan
- career_readiness: how ready this profile is for the target role
Return STRICT JSON: {"overall_summary": "...", "top_3_priorities": [...],
"strengths": [...], "resume_score": 0-100, "ats_score": 0-100,
"career_readiness": 0-100}."""
    user_prompt = f"""Target role: {target_role or 'General software/AI engineering role'}

Full resume text:
{full_context}

Prior tool outputs:
{prior_results}"""
    return call_llm_json(system_prompt, user_prompt)


TOOL_REGISTRY = {
    "skill_gap_analysis": tool_skill_gap_analysis,
    "project_suggestions": tool_project_suggestions,
    "ats_keyword_check": tool_ats_keyword_check,
    # overall_recommendations handled separately in executor.py since it needs prior_results
}