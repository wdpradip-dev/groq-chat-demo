# AI ML Demo — Groq Chat

A Streamlit chat app powered by Groq's ultra-fast LLM inference, with selectable
AI personas and quick-start prompts.

## Features

- **Model picker** — Llama 3.3 70B, Llama 3.1 8B (fastest), Mixtral 8x7B, Gemma 2 9B
- **AI Modes** — General Chat, AI/ML Expert, Python Tutor, Data Analyst, Research Assistant
- **Quick Prompts** — one-click starter questions on AI/ML topics
- **Temperature & max tokens** controls in the sidebar
- **Live stats** — tracks tokens, turns, and response time per session

## Setup

1. Get a free API key at https://console.groq.com/keys
2. Set it as an environment variable:
   - Windows (PowerShell): `$env:GROQ_API_KEY = "your_key_here"`
   - Windows (cmd): `set GROQ_API_KEY=your_key_here`
   - bash: `export GROQ_API_KEY=your_key_here`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## Deploying to Streamlit Community Cloud

Don't commit your API key. Instead, add it under the app's
**Settings → Secrets** on Streamlit Cloud:

```toml
GROQ_API_KEY = "your_key_here"
```

The app reads the key from `st.secrets` first, falling back to the
`GROQ_API_KEY` environment variable for local runs.
