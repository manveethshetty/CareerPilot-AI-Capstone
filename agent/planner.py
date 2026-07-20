"""
Planner: the agentic decision-making step.

Rather than always running every analysis tool in a fixed order, the
Planner is an LLM call that looks at a short resume summary + the user's
target role and decides WHICH tools are relevant and in WHAT order,
returning a structured plan. This is what makes the pipeline "agentic"
rather than a static prompt chain: the control flow itself is a model
decision, not a hardcoded if/else.

Available tools mirror agent/tools.py:
  - skill_gap_analysis
  - project_suggestions
  - ats_keyword_check
  - overall_recommendations
"""
from agent.llm_client import call_llm_json

AVAILABLE_TOOLS = [
    "skill_gap_analysis",
    "project_suggestions",
    "ats_keyword_check",
    "overall_recommendations",
]

PLANNER_SYSTEM_PROMPT = f"""You are the Planner in an agentic resume-analysis workflow.
Given a short resume summary and an optional target role, decide which of
the following tools should run, and in what order, to give the most useful
analysis. Available tools: {AVAILABLE_TOOLS}.

Rules:
- Always include "overall_recommendations" last, since it synthesizes the others.
- Only skip a tool if it is clearly irrelevant (this should be rare — usually all 4 run).
- Return STRICT JSON only, in this shape:
{{"plan": ["tool_name_1", "tool_name_2", ...], "reasoning": "one sentence why this order"}}
"""


def create_plan(resume_summary: str, target_role: str = "") -> dict:
    user_prompt = f"""Resume summary:
{resume_summary}

Target role (may be blank if unspecified): {target_role or "Not specified"}

Decide the tool execution plan."""

    result = call_llm_json(PLANNER_SYSTEM_PROMPT, user_prompt)

    # Safety net: if the model returns something malformed, fall back to running everything
    plan = result.get("plan") if isinstance(result, dict) else None
    if not plan or not all(tool in AVAILABLE_TOOLS for tool in plan):
        plan = AVAILABLE_TOOLS
        result = {"plan": plan, "reasoning": "Fallback: running full default pipeline."}

    return result
