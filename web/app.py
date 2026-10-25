import html
import time
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="WHY — Organizational Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Design system ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#172033; --muted:#667085; --line:#e7eaf0; --panel:#ffffff; --soft:#f5f7fb; --blue:#3559e0; }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
    .stApp { background:#f7f8fc; color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(247,248,252,.88); }
    .block-container { max-width:1320px; padding-top:1.5rem; padding-bottom:3rem; }
    [data-testid="stSidebar"] { background:#101828; border-right:1px solid #273247; }
    [data-testid="stSidebar"] * { color:#edf2ff !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label,
    [data-testid="stSidebar"] [data-testid="stTextInput"] label { color:#b8c4d9 !important; }
    .brand-row { display:flex; align-items:center; gap:12px; margin:0 0 1.2rem 0; }
    .brand-mark { width:46px; height:46px; display:flex; align-items:center; justify-content:center; border-radius:14px; background:linear-gradient(135deg,#627cff,#3449c7); color:white; font-size:24px; box-shadow:0 8px 20px #3559e033; }
    .brand-name { font:800 1.55rem Manrope,sans-serif; letter-spacing:-.05em; color:#172033; line-height:1.05; }
    .brand-sub { color:#7b8498; font-size:.78rem; margin-top:4px; }
    .hero { border-radius:24px; padding:30px 32px; background:radial-gradient(circle at 85% 15%,#394cbb 0,#202f73 26%,#17244e 58%,#111a35 100%); color:white; margin-bottom:20px; position:relative; overflow:hidden; }
    .hero:after { content:' '; position:absolute; width:260px; height:260px; border:1px solid #ffffff18; border-radius:50%; right:-75px; top:-120px; box-shadow:0 0 0 32px #ffffff08,0 0 0 64px #ffffff05; }
    .hero-eyebrow { color:#b9c7ff; text-transform:uppercase; font-size:.72rem; font-weight:700; letter-spacing:.15em; margin-bottom:10px; }
    .hero h1 { color:#fff; font:800 clamp(1.8rem,3vw,2.5rem) Manrope,sans-serif; letter-spacing:-.045em; margin:0 0 10px 0; }
    .hero p { color:#d7defb; font-size:1rem; max-width:690px; margin:0; line-height:1.65; }
    .pill { display:inline-flex; align-items:center; gap:7px; background:#ffffff13; border:1px solid #ffffff25; padding:7px 11px; border-radius:999px; color:#e5eaff; font-size:.76rem; margin-top:19px; }
    .section-title { font:750 1.12rem Manrope,sans-serif; letter-spacing:-.025em; color:#1b2540; margin:0 0 4px 0; }
    .section-help { color:#7b8498; font-size:.86rem; margin:0 0 16px 0; }
    .metric-card { background:white; border:1px solid var(--line); border-radius:17px; padding:17px 18px; min-height:110px; box-shadow:0 2px 8px #17203304; }
    .metric-label { color:#798399; font-size:.78rem; font-weight:600; margin-bottom:10px; }
    .metric-value { color:#1b2540; font:800 1.35rem Manrope,sans-serif; letter-spacing:-.035em; }
    .metric-note { color:#7b8498; font-size:.76rem; margin-top:5px; }
    .surface { background:white; border:1px solid var(--line); border-radius:20px; padding:22px; box-shadow:0 4px 16px #17203305; }
    .answer-label { color:#5267d9; text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:800; margin-bottom:8px; }
    .answer-body { color:#26324a; font-size:1rem; line-height:1.8; }
    .source-chip { display:inline-block; background:#eef2ff; color:#354bc3; border:1px solid #dce3ff; padding:4px 9px; border-radius:7px; font-size:.74rem; font-weight:700; }
    .status-dot { display:inline-block; width:8px; height:8px; background:#3cc28a; border-radius:50%; margin-right:7px; }
    div.stButton > button { border-radius:11px; font-weight:700; min-height:2.7rem; }
    div[data-testid="stFormSubmitButton"] button { border-radius:12px; min-height:3rem; }
    div[data-testid="stFileUploader"] { background:#fafbff; border:1px dashed #cbd3e4; border-radius:15px; padding:12px; }
    .stTextArea textarea { border-radius:13px; background:#fff; }
    .stSelectbox div[data-baseweb="select"] > div { border-radius:10px; }
    [data-testid="stExpander"] { border:1px solid var(--line); border-radius:13px; background:#fff; }
    .footer-note { color:#98a1b2; font-size:.76rem; text-align:center; margin-top:28px; }
    @media (max-width:700px) { .hero { padding:23px; } .block-container { padding-left:1rem; padding-right:1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

API_DEFAULT = "http://127.0.0.1:8000"
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "uploaded_count" not in st.session_state:
    st.session_state.uploaded_count = 0
if "last_uploads" not in st.session_state:
    st.session_state.last_uploads = []


def api_get(url: str, **kwargs: Any):
    return requests.get(url, timeout=kwargs.pop("timeout", 8), **kwargs)


def safe_text(value: Any, fallback: str = "—") -> str:
    if value is None or str(value).strip() == "":
        return fallback
    return str(value)


with st.sidebar:
    st.markdown("<div style='font:800 1.25rem Manrope,sans-serif;letter-spacing:-.04em;margin:8px 0 2px'>🧠 WHY</div><div style='font-size:.78rem;color:#b8c4d9;margin-bottom:22px'>Organizational Memory Intelligence</div>", unsafe_allow_html=True)
    st.markdown("**Workspace settings**")
    api_url = st.text_input("Backend URL", API_DEFAULT, help="FastAPI backend address")
    role = st.selectbox("Preview access as", ["engineer", "intern", "finance", "exec"], index=0)
    st.caption("Demo role filtering only. Production deployments need authenticated identity and server-enforced permissions.")
    st.divider()
    try:
        health_res = api_get(f"{api_url.rstrip('/')}/health", timeout=3)
        backend_ok = health_res.ok
    except requests.RequestException:
        backend_ok = False
    if backend_ok:
        st.markdown("<span class='status-dot'></span>Backend connected", unsafe_allow_html=True)
    else:
        st.warning("Backend offline. Start FastAPI in a separate terminal.")
    st.markdown("<div style='font-size:.75rem;color:#9caac2;margin-top:24px'>HACKATHON BUILD · LOCAL DEMO</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="brand-row">
      <div class="brand-mark">✳</div>
      <div><div class="brand-name">WHY</div><div class="brand-sub">Organizational Memory Intelligence</div></div>
    </div>
    <div class="hero">
      <div class="hero-eyebrow">Your team's collective memory</div>
      <h1>Find the why behind the work.</h1>
      <p>Ask natural-language questions across documents, email threads, chat exports and project history. Get grounded answers with evidence you can inspect—not just a list of files.</p>
      <div class="pill">✦ Evidence-backed answers&nbsp;&nbsp; · &nbsp;&nbsp;Source-level citations&nbsp;&nbsp; · &nbsp;&nbsp;Access-aware retrieval</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Compact status metrics
try:
    sources_response = api_get(f"{api_url.rstrip('/')}/api/sources", params={"role": role}, timeout=8)
    sources_response.raise_for_status()
    visible_sources = sources_response.json().get("sources", [])
except (requests.RequestException, ValueError):
    visible_sources = []

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>AVAILABLE SOURCES</div><div class='metric-value'>{len(visible_sources)}</div><div class='metric-note'>Visible to selected role</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown("<div class='metric-card'><div class='metric-label'>SEARCH STRATEGY</div><div class='metric-value'>Hybrid search</div><div class='metric-note'>Keyword + semantic retrieval</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown("<div class='metric-card'><div class='metric-label'>ANSWER STANDARD</div><div class='metric-value'>Evidence first</div><div class='metric-note'>Inspect source excerpts before trusting</div></div>", unsafe_allow_html=True)

st.write("")
tab_ask, tab_upload, tab_library, tab_about = st.tabs(["✦  Ask WHY", "＋  Add knowledge", "▤  Source library", "ⓘ  About this demo"])

with tab_ask:
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown("<div class='section-title'>Ask a question</div><div class='section-help'>Explore decisions, rationale, owners, changes and unresolved questions.</div>", unsafe_allow_html=True)
        sample_questions = [
            "Why did we choose this architecture, and what alternatives were considered?",
            "Summarize the key changes and pending action items in the latest email thread.",
            "What changed in this decision over time?",
            "What is still unresolved, and what evidence supports that?",
            "What was the final production deployment date?",
        ]
        selected_sample = st.selectbox("Start with an example", ["Choose a question…"] + sample_questions, label_visibility="collapsed")
        with st.form("ask_form", clear_on_submit=False):
            question = st.text_area(
                "Your question",
                value="" if selected_sample == "Choose a question…" else selected_sample,
                placeholder="e.g. What did we decide, why, and what evidence supports it?",
                height=112,
                label_visibility="collapsed",
            )
            ask_button = st.form_submit_button("Find the evidence  →", type="primary", use_container_width=True)
        st.caption("Tip: ask a focused question first. Follow up on a cited source to dig deeper.")

        if ask_button:
            if len(question.strip()) < 3:
                st.warning("Please enter a little more detail in your question.")
            elif not backend_ok:
                st.error("The backend is not reachable. Start FastAPI, then try again.")
            else:
                start = time.perf_counter()
                try:
                    with st.spinner("Searching authorized sources and preparing an evidence-based answer…"):
                        response = requests.post(
                            f"{api_url.rstrip('/')}/api/ask",
                            json={"question": question.strip(), "role": role},
                            timeout=(5, 180),
                        )
                        response.raise_for_status()
                        answer_data = response.json()
                    answer_data["elapsed_seconds"] = round(time.perf_counter() - start, 1)
                    answer_data["question"] = question.strip()
                    st.session_state.last_answer = answer_data
                except requests.Timeout:
                    st.error("The request timed out. Check the FastAPI terminal to see whether retrieval or LLM generation is taking too long.")
                except requests.RequestException as exc:
                    detail = ""
                    try:
                        detail = response.text  # type: ignore[name-defined]
                    except Exception:
                        pass
                    st.error(f"The backend request failed: {exc}. {detail[:500]}")
                except ValueError:
                    st.error("The backend returned a response that was not valid JSON.")

    with right:
        st.markdown("<div class='section-title'>Questions worth asking</div><div class='section-help'>Designed to test memory, reasoning and trust.</div>", unsafe_allow_html=True)
        prompt_cards = [
            ("Decision history", "What alternatives were considered, and why was the final option chosen?", "↗"),
            ("Action items", "List pending actions and name an owner only when the source specifies one.", "✓"),
            ("Conflicting facts", "Do any sources disagree? Show both claims and their dates.", "⚖"),
            ("Knowledge gaps", "What information is missing to answer this confidently?", "⌕"),
        ]
        for title, prompt, symbol in prompt_cards:
            with st.container(border=True):
                c1, c2 = st.columns([.15, .85])
                with c1:
                    st.markdown(f"<div style='font-size:1.25rem;color:#5267d9;padding-top:2px'>{symbol}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**{title}**")
                    st.caption(prompt)

    # Render answer outside the form so it remains visible after reruns.
    answer = st.session_state.last_answer
    if answer:
        st.write("")
        st.markdown("<div class='section-title'>Answer & evidence</div><div class='section-help'>Review the response and open each citation to inspect its supporting excerpt.</div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<div class='answer-label'>✦ GROUNDED RESPONSE · {answer.get('elapsed_seconds', '—')}s</div>", unsafe_allow_html=True)
            st.markdown(answer.get("answer", "No answer returned."))
            if answer.get("insufficient_evidence"):
                st.warning("Insufficient evidence: this answer should be treated as unresolved.")
            sources = answer.get("sources", [])
            st.divider()
            st.markdown(f"**Evidence cited** · {len(sources)} source snippet(s)")
            if not sources:
                st.info("No authorized source snippets were returned. Try a more specific question or check the role permissions.")
            for index, source in enumerate(sources, start=1):
                sid = safe_text(source.get("id"), str(index))
                title = safe_text(source.get("title"), "Untitled source")
                kind = safe_text(source.get("source_type"), "source")
                timestamp = safe_text(source.get("timestamp"), "Date unknown")
                with st.expander(f"[{sid}]  {title}  ·  {kind}  ·  {timestamp}", expanded=(index == 1)):
                    st.caption(f"Document ID: {safe_text(source.get('document_id'))}")
                    st.markdown("**Source excerpt**")
                    st.write(source.get("excerpt", "No excerpt was returned."))
                    if source.get("url"):
                        st.markdown(f"[Open original source ↗]({source['url']})")
        if st.button("Clear answer", key="clear_answer"):
            st.session_state.last_answer = None
            st.rerun()

with tab_upload:
    st.markdown("<div class='section-title'>Add knowledge to WHY</div><div class='section-help'>Upload public or synthetic sample data for the hackathon. Avoid confidential or personal information.</div>", unsafe_allow_html=True)
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Drop files here or browse",
            type=["pdf", "txt", "md", "markdown", "log", "eml", "json", "csv", "docx"],
            accept_multiple_files=True,
            help="Up to 20 MB per file. Scanned PDFs need OCR; searchable PDFs work directly.",
            key="knowledge_upload",
        )
        uc1, uc2 = st.columns(2)
        with uc1:
            upload_type = st.selectbox(
                "Source type",
                ["auto", "email", "chat", "meeting", "doc", "github"],
                format_func=lambda x: {"auto": "Auto-detect", "email": "Email thread", "chat": "Slack / chat export", "meeting": "Meeting transcript", "doc": "Document / PDF", "github": "GitHub / PR history"}[x],
            )
        with uc2:
            upload_access = st.selectbox(
                "Access classification",
                ["public", "engineering", "finance", "exec"],
                format_func=lambda x: {"public": "Everyone (public)", "engineering": "Engineering only", "finance": "Finance only", "exec": "Executive / admin"}[x],
            )
        st.caption("Supported: PDF, TXT, Markdown, EML, JSON, CSV and DOCX. Direct Slack/Gmail connections are not configured in this demo.")
        do_upload = st.button("Upload and index files", type="primary", use_container_width=True, disabled=not uploaded_files or not backend_ok)
        if do_upload:
            for file in uploaded_files:
                try:
                    with st.spinner(f"Indexing {file.name}…"):
                        res = requests.post(
                            f"{api_url.rstrip('/')}/api/upload",
                            files={"file": (file.name, file.getvalue(), file.type or "application/octet-stream")},
                            data={"source_type": upload_type, "access_role": upload_access},
                            timeout=(10, 240),
                        )
                    if res.ok:
                        payload = res.json()
                        st.success(f"{file.name} · {payload.get('chunks_created', 0)} chunks · {payload.get('message', 'Indexed successfully')}")
                        st.session_state.uploaded_count += 1
                        st.session_state.last_uploads.append(file.name)
                    else:
                        try:
                            message = res.json().get("detail", res.text)
                        except ValueError:
                            message = res.text
                        st.error(f"{file.name}: {message}")
                except requests.Timeout:
                    st.error(f"{file.name}: upload/indexing timed out. Check the backend terminal.")
                except requests.RequestException as exc:
                    st.error(f"{file.name}: could not reach backend: {exc}")
            st.info("Upload processing finished. Return to Ask WHY and test a question grounded in the uploaded file.")
    if st.session_state.last_uploads:
        st.markdown("**Recently uploaded in this session**")
        for name in st.session_state.last_uploads[-5:]:
            st.markdown(f"- `{name}`")

with tab_library:
    st.markdown("<div class='section-title'>Source library</div><div class='section-help'>Documents visible to the currently selected demo role.</div>", unsafe_allow_html=True)
    refresh = st.button("↻ Refresh sources", key="refresh_sources")
    try:
        library_response = api_get(f"{api_url.rstrip('/')}/api/sources", params={"role": role}, timeout=10)
        library_response.raise_for_status()
        library_sources = library_response.json().get("sources", [])
        if not library_sources:
            st.info("No sources are visible for this role yet. Upload a document or run the sample corpus ingestion.")
        else:
            st.caption(f"{len(library_sources)} visible source(s)")
            for source in library_sources:
                title = safe_text(source.get("title"), "Untitled source")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2.2, 1, 1.2])
                    c1.markdown(f"**{title}**")
                    c1.caption(f"ID: {source.get('id', '—')} · Author: {safe_text(source.get('author'))}")
                    c2.markdown(f"`{safe_text(source.get('source_type'))}`")
                    c3.caption(safe_text(source.get("timestamp"), "Date unknown"))
                    if source.get("url"):
                        st.markdown(f"[Open source ↗]({source['url']})")
    except (requests.RequestException, ValueError) as exc:
        st.error(f"Could not load the source library: {exc}")

with tab_about:
    st.markdown("<div class='section-title'>Built for trustworthy organizational memory</div><div class='section-help'>A hackathon prototype for recovering context behind decisions—not just finding files.</div>", unsafe_allow_html=True)
    about1, about2 = st.columns(2)
    with about1:
        with st.container(border=True):
            st.markdown("### What it demonstrates")
            st.markdown("- Multi-format document ingestion\n- Hybrid keyword + vector retrieval\n- Answers with inspectable source excerpts\n- Demo role-based retrieval filtering\n- Local LLM option via Ollama")
    with about2:
        with st.container(border=True):
            st.markdown("### Current prototype limits")
            st.markdown("- Scanned PDF OCR is not enabled\n- No direct Slack or email account connector\n- Timeline endpoint lists source metadata, not extracted decision events\n- Role selector is not production authentication\n- Validate citation correctness with a benchmark before judging")

st.markdown("<div class='footer-note'>WHY · Organizational Memory Intelligence · Built to make decisions searchable, explainable and verifiable.</div>", unsafe_allow_html=True)
