import os
import streamlit as st
from groq import Groq
import time

st.set_page_config(
    page_title="AI ML Demo — Groq",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #6b7280; font-size: 1rem; margin-bottom: 1.5rem; }
    .stat-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .stat-number { font-size: 1.8rem; font-weight: 700; color: #6366f1; }
    .stat-label { font-size: 0.8rem; color: #9ca3af; }
</style>
""", unsafe_allow_html=True)

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is not set. Add it to Streamlit secrets (Cloud) or your environment (local).")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
}

AI_MODES = {
    "💬 General Chat": "You are a helpful, concise AI assistant.",
    "🧠 AI/ML Expert": (
        "You are an expert in Artificial Intelligence and Machine Learning. "
        "Explain concepts clearly with examples and code snippets when relevant."
    ),
    "🐍 Python Tutor": (
        "You are an expert Python developer and tutor. Provide clean, well-explained "
        "Python code examples and explain best practices."
    ),
    "📊 Data Analyst": (
        "You are a data analysis expert. Help users understand data, statistics, "
        "visualization, and analytical approaches. Use pandas, numpy, and matplotlib examples."
    ),
    "🔬 Research Assistant": (
        "You are a research assistant specializing in AI/ML papers and concepts. "
        "Summarize, explain, and connect ideas from the latest AI research."
    ),
}

QUICK_PROMPTS = [
    "Explain neural networks simply",
    "What is transformer architecture?",
    "Python code for linear regression",
    "Supervised vs unsupervised learning?",
    "How does RAG work?",
    "Explain gradient descent",
]

# ── Session state init ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_tokens": 0, "turns": 0, "total_time": 0.0}
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    model_name = st.selectbox("Model", list(MODELS.keys()), index=0)
    model_id = MODELS[model_name]

    mode_name = st.selectbox("AI Mode", list(AI_MODES.keys()), index=1)
    system_prompt = AI_MODES[mode_name]

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05,
                            help="Higher = more creative")
    max_tokens = st.slider("Max Tokens", 256, 4096, 1024, 128)

    st.divider()
    st.markdown("### 🚀 Quick Prompts")
    for qp in QUICK_PROMPTS:
        if st.button(qp, use_container_width=True, key=f"qp_{qp}"):
            st.session_state.pending_prompt = qp

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.stats = {"total_tokens": 0, "turns": 0, "total_time": 0.0}
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        "<div style='text-align:center;color:#9ca3af;font-size:0.75rem;margin-top:8px'>"
        "Powered by <b>Groq</b> ⚡ Ultra-fast LLM inference"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🤖 AI/ML Demo Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Powered by Groq · Lightning-fast inference · Multiple AI modes</div>',
    unsafe_allow_html=True,
)

# ── Stats row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
avg_t = st.session_state.stats["total_time"] / max(st.session_state.stats["turns"], 1)
for col, num, label in [
    (c1, st.session_state.stats["turns"], "Turns"),
    (c2, f'{st.session_state.stats["total_tokens"]:,}', "Tokens"),
    (c3, f"{avg_t:.2f}s", "Avg Time"),
    (c4, "⚡", model_name.split("(")[0].strip()),
]:
    col.markdown(
        f'<div class="stat-card"><div class="stat-number">{num}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.divider()

# ── Chat history ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "meta" in msg:
            m = msg["meta"]
            st.caption(f"⏱ {m['time']:.2f}s · ~{m['tokens']} tokens · ⚡ {m['tps']:.0f} tok/s")

# ── Resolve prompt (chat input OR quick-prompt button) ────────────────────────
user_input = st.chat_input("Ask anything about AI, ML, Python, Data Science…")

# quick-prompt button wins only when no direct input this turn
prompt = user_input or st.session_state.pending_prompt
if user_input:
    # clear any stale pending prompt when user types directly
    st.session_state.pending_prompt = None
elif st.session_state.pending_prompt:
    st.session_state.pending_prompt = None  # consume it

# ── Generate response ─────────────────────────────────────────────────────────
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        start = time.time()

        try:
            payload = [{"role": "system", "content": system_prompt}] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            stream = client.chat.completions.create(
                model=model_id,
                messages=payload,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token is not None:
                    full_response += token
                    placeholder.markdown(full_response + "▌")

            elapsed = time.time() - start
            word_count = len(full_response.split())
            tps = word_count / max(elapsed, 0.001)

            placeholder.markdown(full_response)
            st.caption(f"⏱ {elapsed:.2f}s · ~{word_count} tokens · ⚡ {tps:.0f} tok/s")

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "meta": {"time": elapsed, "tokens": word_count, "tps": tps},
            })
            st.session_state.stats["turns"] += 1
            st.session_state.stats["total_tokens"] += word_count
            st.session_state.stats["total_time"] += elapsed

        except Exception as e:
            placeholder.error(f"❌ Groq API error: {e}")
