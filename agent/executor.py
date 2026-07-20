"""
Executor: takes the Planner's ordered tool list and runs each tool in
sequence, passing accumulated results forward (needed for
overall_recommendations, which synthesizes everything before it).
This is the Planner -> Executor pattern reused from AstraMind Travel Agent.
"""
from agent.tools import TOOL_REGISTRY, tool_overall_recommendations


def run_plan(plan: list[str], retriever, target_role: str) -> dict:
    results = {}

    for tool_name in plan:
        if tool_name == "overall_recommendations":
            results["overall_recommendations"] = tool_overall_recommendations(
                retriever, target_role, prior_results=results
            )
        elif tool_name in TOOL_REGISTRY:
            results[tool_name] = TOOL_REGISTRY[tool_name](retriever, target_role)
        else:
            # Unknown tool name from a malformed plan — skip safely
            continue

    return results
