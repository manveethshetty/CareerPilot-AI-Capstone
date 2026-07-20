"""
Thin wrapper around the Groq API, consistent with the AstraMind Groq
call pattern used in earlier bootcamp projects. Centralized here so the
Planner and Executor don't duplicate client setup.
"""
import os
import json
from groq import Groq

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not found. Set it in your .env file or Streamlit secrets."
        )
    return Groq(api_key=api_key)


def call_llm(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL,
             temperature: float = 0.4, json_mode: bool = False) -> str:
    client = get_client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return completion.choices[0].message.content


def call_llm_json(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """Calls the LLM in JSON mode and safely parses the result."""
    raw = call_llm(system_prompt, user_prompt, model=model, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: strip markdown fences if the model added them anyway
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        return json.loads(cleaned)
