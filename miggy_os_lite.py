import os
import json
from typing import Dict, List

import requests
import streamlit as st


APP_TITLE = "Miggy OS Lite — Every Essay to Social Engine"


def call_openai_compatible(messages: List[Dict[str, str]], model: str, api_key: str, base_url: str) -> str:
    """
    Calls an OpenAI-compatible chat completions endpoint.
    Defaults work with OpenAI, OpenRouter, and many compatible providers.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


DECOMPOSE_PROMPT = """You are an elite editorial strategist for an AI-native media company.

Your job is to decompose source material into the most socially useful building blocks.

Return valid JSON with exactly these keys:
- core_thesis: string
- strongest_line: string
- contrarian_take: string
- emotional_angle: string
- debate_angle: string
- key_insights: array of 3 to 5 strings
- likely_audience_segments: array of strings
- social_wedges: array of 3 strings

Rules:
- Be sharp, concise, and non-generic.
- Prefer language that feels internet-native but not cringe.
- Avoid cliches.
- Do not include markdown fences.
"""

CONTENT_PROMPT = """You are Head of Social at an AI-native media company.

Using the structured decomposition below, create socially-native content outputs.

Return valid JSON with exactly these keys:
- tweets: array of 3 strings
- thread: array of 4 strings
- founder_post: string
- video_script: string
- replies: array of 5 strings

Requirements:
- Make each tweet meaningfully different.
- The thread should feel coherent and escalating.
- The founder post should be opinionated and authoritative.
- The video script should be 30 to 45 seconds and spoken naturally.
- Replies should be good enough to use in live conversations.
- Do not include markdown fences.

Structured decomposition:
{decomposition}
"""

DISTRIBUTION_PROMPT = """You are designing a 48-hour distribution plan for an AI-native company.

Using the decomposition and generated content below, return valid JSON with exactly these keys:
- primary_post: string
- posting_sequence: array of objects with keys "time_window", "account", "asset", "goal"
- amplification_moves: array of 4 strings
- what_to_measure: array of 5 strings
- best_bet: string

Requirements:
- Distinguish between brand account and founder/executive account.
- Think in compounding attention, not one-off posting.
- Keep it practical and specific.
- Do not include markdown fences.

Decomposition:
{decomposition}

Content:
{content}
"""


def safe_json_loads(text: str):
    text = text.strip()
    # remove accidental code fences if model adds them
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def render_json_block(title: str, data):
    st.subheader(title)
    st.json(data, expanded=True)


st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Paste an article or essay, then generate decomposition, social outputs, and a 48-hour distribution plan.")

with st.sidebar:
    st.header("Model Settings")
    api_key = st.text_input("API key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    base_url = st.text_input("Base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    st.markdown("---")
    st.write("Use any OpenAI-compatible provider.")
    st.write("Examples:")
    st.code("OpenAI base URL: https://api.openai.com/v1")
    st.code("OpenRouter base URL: https://openrouter.ai/api/v1")

sample_text = """Every publishes a smart essay about how AI changes work.
The article argues that the real shift is not that AI replaces labor outright, but that it changes the shape of leverage.
People who know how to direct models, critique output, and package ideas will outperform people who only execute linearly.
The piece also argues that most teams still use AI for speed, not for rethinking workflows.
The best operators are rebuilding systems around AI, not just plugging AI into old systems.
"""

source_text = st.text_area("Source material", value=sample_text, height=300, placeholder="Paste the essay, article, transcript, or memo here...")

col1, col2, col3 = st.columns(3)
run_decompose = col1.button("1. Decompose")
run_content = col2.button("2. Generate Content")
run_plan = col3.button("3. Build Distribution Plan")

if "decomposition" not in st.session_state:
    st.session_state.decomposition = None
if "content" not in st.session_state:
    st.session_state.content = None
if "plan" not in st.session_state:
    st.session_state.plan = None

if run_decompose:
    if not api_key.strip():
        st.error("Enter an API key in the sidebar.")
    else:
        with st.spinner("Decomposing source material..."):
            try:
                out = call_openai_compatible(
                    messages=[
                        {"role": "system", "content": DECOMPOSE_PROMPT},
                        {"role": "user", "content": source_text},
                    ],
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                )
                st.session_state.decomposition = safe_json_loads(out)
                st.success("Decomposition complete.")
            except Exception as e:
                st.error(f"Failed to decompose: {e}")

if run_content:
    if not st.session_state.decomposition:
        st.warning("Run decomposition first.")
    elif not api_key.strip():
        st.error("Enter an API key in the sidebar.")
    else:
        with st.spinner("Generating social assets..."):
            try:
                out = call_openai_compatible(
                    messages=[
                        {"role": "system", "content": CONTENT_PROMPT.format(decomposition=json.dumps(st.session_state.decomposition, ensure_ascii=False, indent=2))},
                        {"role": "user", "content": "Generate the content outputs now."},
                    ],
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                )
                st.session_state.content = safe_json_loads(out)
                st.success("Content generated.")
            except Exception as e:
                st.error(f"Failed to generate content: {e}")

if run_plan:
    if not st.session_state.decomposition or not st.session_state.content:
        st.warning("Run decomposition and content generation first.")
    elif not api_key.strip():
        st.error("Enter an API key in the sidebar.")
    else:
        with st.spinner("Building distribution plan..."):
            try:
                out = call_openai_compatible(
                    messages=[
                        {
                            "role": "system",
                            "content": DISTRIBUTION_PROMPT.format(
                                decomposition=json.dumps(st.session_state.decomposition, ensure_ascii=False, indent=2),
                                content=json.dumps(st.session_state.content, ensure_ascii=False, indent=2),
                            ),
                        },
                        {"role": "user", "content": "Build the distribution plan now."},
                    ],
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                )
                st.session_state.plan = safe_json_loads(out)
                st.success("Distribution plan generated.")
            except Exception as e:
                st.error(f"Failed to build distribution plan: {e}")

if st.session_state.decomposition:
    render_json_block("Decomposition", st.session_state.decomposition)

if st.session_state.content:
    render_json_block("Social Outputs", st.session_state.content)

if st.session_state.plan:
    render_json_block("48-Hour Distribution Plan", st.session_state.plan)

st.markdown("---")
st.subheader("Suggested submission framing")
st.code(
"""I built a lightweight agent that turns a single essay into a social engine.

It:
1. decomposes the source into narrative wedges,
2. generates native platform outputs,
3. creates a 48-hour distribution plan across brand and founder surfaces.

This is a simplified version of how I think about social: not as output, but as infrastructure that compounds.""",
language="markdown",
)
