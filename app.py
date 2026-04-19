import streamlit as st
import time
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root & Background ── */
:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #252535;
    --accent: #6c63ff;
    --accent2: #ff6584;
    --accent3: #43e97b;
    --text: #e8e8f0;
    --muted: #6b6b85;
    --card-shadow: 0 4px 32px rgba(108,99,255,0.08);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(108,99,255,0.12) 0%, transparent 70%),
                var(--bg) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

/* ── Hide default elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem !important; max-width: 1200px; }

/* ── Typography ── */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* ── Hero Section ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: rgba(108,99,255,0.15);
    border: 1px solid rgba(108,99,255,0.3);
    color: #a89dff;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 0 0 1rem 0;
    background: linear-gradient(135deg, #fff 30%, #a89dff 70%, #6c63ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    font-weight: 300;
    max-width: 520px;
    margin: 0 auto 2rem auto;
    line-height: 1.7;
}

/* ── Search Card ── */
.search-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--card-shadow);
    position: relative;
    overflow: hidden;
}
.search-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}

/* ── Streamlit Input Overrides ── */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 2rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(108,99,255,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Step Cards ── */
.step-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
.step-card.active { border-color: rgba(108,99,255,0.5); }
.step-card.done { border-color: rgba(67,233,123,0.3); }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 0.6rem;
}
.step-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.step-icon.search { background: rgba(108,99,255,0.2); }
.step-icon.reader { background: rgba(255,101,132,0.2); }
.step-icon.writer { background: rgba(255,200,80,0.2); }
.step-icon.critic { background: rgba(67,233,123,0.2); }

.step-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
}

/* ── Result Panels ── */
.result-panel {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #b0b0cc;
    line-height: 1.7;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Report Panel ── */
.report-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.report-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent3), #38d9a9);
}
.report-content {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.97rem;
    line-height: 1.85;
    color: var(--text);
    white-space: pre-wrap;
}

/* ── Score Badge ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(67,233,123,0.12);
    border: 1px solid rgba(67,233,123,0.25);
    color: var(--accent3);
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    padding: 0.5rem 1.2rem;
    border-radius: 100px;
    margin-bottom: 1rem;
}

/* ── Critic Panel ── */
.critic-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.critic-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent2), #f97316);
}
.critic-content {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
}

/* ── Divider ── */
.section-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
}
.section-divider-line { flex: 1; height: 1px; background: var(--border); }
.section-divider-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
}

/* ── Pipeline Status Row ── */
.pipeline-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0;
    font-size: 0.88rem;
    color: var(--muted);
}
.pipeline-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--border);
    flex-shrink: 0;
}
.pipeline-dot.active {
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 1.2s infinite;
}
.pipeline-dot.done { background: var(--accent3); }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* ── Spinner override ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Expander ── */
details summary {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--muted) !important;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper: render a step card ─────────────────────────────────────────────────
def step_card(icon, icon_class, label, title, content=None, status="idle"):
    css_class = "active" if status == "active" else ("done" if status == "done" else "")
    st.markdown(f"""
    <div class="step-card {css_class}">
        <div class="step-header">
            <div class="step-icon {icon_class}">{icon}</div>
            <div>
                <div class="step-label">{label}</div>
                <div class="step-title">{title}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if content:
        st.markdown(f'<div class="result-panel">{content}</div>', unsafe_allow_html=True)


def section_divider(label):
    st.markdown(f"""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">{label}</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


# ─── Run Pipeline ────────────────────────────────────────────────────────────────
def run_pipeline(topic: str):
    state = {}

    # ── Step 1: Search ──
    with st.container():
        step_placeholder = st.empty()
        step_placeholder.markdown("""
        <div class="step-card active">
            <div class="step-header">
                <div class="step-icon search">🔍</div>
                <div>
                    <div class="step-label">Step 01 · Running</div>
                    <div class="step-title">Search Agent — scanning the web...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_result"] = search_result['messages'][-1].content

        step_placeholder.markdown("""
        <div class="step-card done">
            <div class="step-header">
                <div class="step-icon search">✅</div>
                <div>
                    <div class="step-label">Step 01 · Complete</div>
                    <div class="step-title">Search Agent — results gathered</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View search results"):
            st.markdown(f'<div class="result-panel">{state["search_result"][:2000]}</div>', unsafe_allow_html=True)

    # ── Step 2: Reader ──
    with st.container():
        step_placeholder2 = st.empty()
        step_placeholder2.markdown("""
        <div class="step-card active">
            <div class="step-header">
                <div class="step-icon reader">📖</div>
                <div>
                    <div class="step-label">Step 02 · Running</div>
                    <div class="step-title">Reader Agent — scraping top source...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_result'][:800]}")]
        })
        state["scraped_content"] = reader_result['messages'][-1].content

        step_placeholder2.markdown("""
        <div class="step-card done">
            <div class="step-header">
                <div class="step-icon reader">✅</div>
                <div>
                    <div class="step-label">Step 02 · Complete</div>
                    <div class="step-title">Reader Agent — content extracted</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View scraped content"):
            st.markdown(f'<div class="result-panel">{state["scraped_content"][:2000]}</div>', unsafe_allow_html=True)

    # ── Step 3: Writer ──
    with st.container():
        step_placeholder3 = st.empty()
        step_placeholder3.markdown("""
        <div class="step-card active">
            <div class="step-header">
                <div class="step-icon writer">✍️</div>
                <div>
                    <div class="step-label">Step 03 · Running</div>
                    <div class="step-title">Writer Chain — drafting report...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        research_combined = (
            f"SEARCH RESULTS:\n{state['search_result']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        step_placeholder3.markdown("""
        <div class="step-card done">
            <div class="step-header">
                <div class="step-icon writer">✅</div>
                <div>
                    <div class="step-label">Step 03 · Complete</div>
                    <div class="step-title">Writer Chain — report ready</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Step 4: Critic ──
    with st.container():
        step_placeholder4 = st.empty()
        step_placeholder4.markdown("""
        <div class="step-card active">
            <div class="step-header">
                <div class="step-icon critic">🧐</div>
                <div>
                    <div class="step-label">Step 04 · Running</div>
                    <div class="step-title">Critic Chain — evaluating report...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        state["feedback"] = critic_chain.invoke({"report": state["report"]})

        step_placeholder4.markdown("""
        <div class="step-card done">
            <div class="step-header">
                <div class="step-icon critic">✅</div>
                <div>
                    <div class="step-label">Step 04 · Complete</div>
                    <div class="step-title">Critic Chain — review done</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return state


# ─── Main App ────────────────────────────────────────────────────────────────────
def main():
    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">⚡ Multi-Agent Research Pipeline</div>
        <h1 class="hero-title">ResearchMind AI</h1>
        <p class="hero-sub">Enter any topic and watch four specialized AI agents collaborate to deliver a structured, peer-reviewed research report.</p>
    </div>
    """, unsafe_allow_html=True)

    # Search Card
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        topic = st.text_input(
            "",
            placeholder="e.g. Quantum computing applications in drug discovery...",
            label_visibility="collapsed",
            key="topic_input"
        )
    with col2:
        run = st.button("Research →", key="run_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    # Pipeline flow description
    st.markdown("""
    <div style="display:flex; gap:1.5rem; justify-content:center; margin-bottom:2rem; flex-wrap:wrap;">
        <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#6b6b85;">🔍 Search Agent</span>
        <span style="color:#252535;">→</span>
        <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#6b6b85;">📖 Reader Agent</span>
        <span style="color:#252535;">→</span>
        <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#6b6b85;">✍️ Writer Chain</span>
        <span style="color:#252535;">→</span>
        <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#6b6b85;">🧐 Critic Chain</span>
    </div>
    """, unsafe_allow_html=True)

    if run and topic.strip():
        section_divider("Pipeline Execution")

        with st.spinner(""):
            state = run_pipeline(topic.strip())

        # ── Final Report ──
        section_divider("Research Report")
        st.markdown(f"""
        <div class="report-panel">
            <div class="report-content">{state['report']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇ Download Report (.txt)",
            data=state["report"],
            file_name=f"report_{topic[:30].replace(' ','_')}.txt",
            mime="text/plain",
        )

        # ── Critic Review ──
        section_divider("Critic Review")
        st.markdown(f"""
        <div class="critic-panel">
            <div class="critic-content">{state['feedback']}</div>
        </div>
        """, unsafe_allow_html=True)

    elif run and not topic.strip():
        st.warning("Please enter a research topic first.")


if __name__ == "__main__":
    main()