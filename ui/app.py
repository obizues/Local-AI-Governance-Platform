import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import difflib
import pandas as pd
import faiss
import re
import time
print("DEBUG: Starting import of sentence_transformers and transformers", flush=True)
from sentence_transformers import SentenceTransformer
from transformers import pipeline
print("DEBUG: Finished import of sentence_transformers and transformers", flush=True)


# Placeholder variable definitions (replace with actual logic as needed)
GEN_MODEL_NAME = 'gpt2'
GEN_MODEL_NAME_DISPLAY = 'GPT-2'
ECHO_MODE = False
salary_pattern = re.compile(r"\$[0-9,]+")





# Global fuzzy_any function for fuzzy matching
def fuzzy_any(targets, query_lc, cutoff=0.7):
    for t in targets:
        if difflib.SequenceMatcher(None, t, query_lc).ratio() >= cutoff:
            return True
        words = query_lc.split()
        for w in words:
            if difflib.SequenceMatcher(None, t, w).ratio() >= cutoff:
                return True
    return False

def write_audit_log(message):
    with open('access_audit.log', 'a', encoding='utf-8') as audit_log:
        audit_log.write(message)

# --- Top blue app title bar ---
st.markdown(
    """
    <style>
            margin: 0 auto 0 auto;
            padding: 0.7em 0 0.7em 0;
            box-sizing: border-box;
            border-radius: 0 0 16px 16px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
            letter-spacing: 0.01em;
            max-width: 700px;
        # end dept_map
        .top-title-banner { font-size: 1.3em; }
    </style>
    <div class="top-title-banner">
        &#129302; Local AI Chatbot POC
    </div>
    """, unsafe_allow_html=True)



import pandas as pd
import re
import time
import difflib
from llm_backend.model_service import load_embed_model, load_llm_pipeline, load_faiss_index, load_metadata

# Placeholder variable definitions (replace with actual logic as needed)
GEN_MODEL_NAME = 'gpt2'
GEN_MODEL_NAME_DISPLAY = 'GPT-2'
ECHO_MODE = False
salary_pattern = re.compile(r"\$[0-9,]+")

app_title_banner = """
<style>
.app-title-banner {
    background: #f5f5f5;
    color: #222;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 1.08em;
    font-weight: 500;
    text-align: center;
    margin: 0.5em auto 0 auto;
    padding: 0.5em 0 0.5em 0;
    box-sizing: border-box;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
    max-width: 700px;
}
.app-title-banner .name-title {
    font-size: 1.18em;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 0.1em;
}
.app-title-banner .subtitle {
    font-size: 0.98em;
    color: #1976d2;
    margin-bottom: 0.2em;
}
.app-title-banner .links, .app-title-banner .project-links {
    font-size: 0.97em;
    margin-bottom: 0.1em;
}
.app-title-banner a {
    color: #1976d2;
    text-decoration: underline;
    margin: 0 8px;
    font-size: 0.97em;
}
.app-title-banner .project-links {
    margin-top: 0.1em;
}
    @media (max-width: 600px) {
        .app-title-banner { font-size: 0.93em; }
        .app-title-banner .name-title { font-size: 1em; }
        .app-title-banner .subtitle { font-size: 0.91em; }
        .app-title-banner .links, .app-title-banner .project-links { font-size: 0.91em; }
    }
</style>

<div class="app-title-banner">
    <div class="name-title" style="font-size:0.95em; font-weight:400; margin-bottom:0.08em; text-align:center; color:#1976d2;"><b>Chris Obermeier</b> | SVP of Engineering</div>
    <div class="subtitle" style="background:transparent;border-radius:0;padding:2px 8px;font-size:0.83em;text-align:center;margin-bottom:0.08em;color:#64b5f6;font-weight:400;">Enterprise &amp; PE-Backed Platform Modernization | AI &amp; Data-Driven Transformation</div>
    <div class="links" style="font-size:0.92em; font-weight:400; margin-bottom:0em; text-align:center;">
        <a href="https://www.linkedin.com/in/chrisobermeier/" target="_blank">LinkedIn</a> |
        <a href="https://github.com/obizues" target="_blank">GitHub</a> |
        <a href="mailto:chris.obermeier@gmail.com" target="_blank">Email</a>
    </div>
    <div class="project-links" style="font-size:0.92em; font-weight:400; margin-top:0em; text-align:center;">
        <span style="margin-right:4px;">&#11088;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC" target="_blank">Star on GitHub</a> |
        <span style="margin-right:4px;">&#128214;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md" target="_blank">Read Documentation</a> |
        <span style="margin-right:4px;">&#127891;</span><a href="https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md" target="_blank">View Architecture</a>
    </div>
</div>
"""
st.markdown(app_title_banner, unsafe_allow_html=True)

# --- RBAC: Role selection ---

ROLES = [
    "Alice Johnson (HR)",
    "David Kim (Engineer)",
    "Olivia Zhang (CTO)",
]
ROLE_DESCRIPTIONS = {
    "Alice Johnson (HR)": "Access to confidential HR details (e.g., pay, benefits)",
    "David Kim (Engineer)": "Access to David Kim's engineering SOPs and salary only",
    "Olivia Zhang (CTO)": "Full access to all Technology department data and documents"
}

if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ROLES[0]




# --- Model caching using Streamlit's cache_resource ---


EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
embed_model = load_embed_model()
llm, gen_model_display = load_llm_pipeline(GEN_MODEL_NAME)



# All model loading is now handled by the cached functions above:

# Model and data loading (now via backend service)
embed_model = load_embed_model()

# Model selection logic: only load LLM pipeline when model changes
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = 'gpt2'
if 'llm' not in st.session_state or 'gen_model_display' not in st.session_state:
    st.session_state['llm'], st.session_state['gen_model_display'] = load_llm_pipeline(st.session_state['selected_model'])

# Data loading

project_root = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(project_root, '..', 'vector_db', 'faiss_index.bin')
metadata_path = os.path.join(project_root, '..', 'vector_db', 'metadata.csv')
chunks_path = os.path.join(project_root, '..', 'ingestion', 'document_chunks.csv')

faiss_index = load_faiss_index(index_path)
metadata = load_metadata(metadata_path)
# --- Move retrieve and generate_answer above chat UI ---
# --- Load FAISS index and metadata ---
import numpy as np
import os
import streamlit as st
index_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'document_chunks.index')
metadata_path = os.path.join(os.path.dirname(__file__), '..', 'vector_db', 'metadata.csv')
chunks_path = os.path.join(os.path.dirname(__file__), '..', 'ingestion', 'document_chunks.csv')

# Only initialize metadata and index once per session
print(f"DEBUG: loading metadata from: {metadata_path}", flush=True)
if 'metadata' not in st.session_state:
    if os.path.exists(metadata_path):
        import os
        abs_path = os.path.abspath(metadata_path)
        print(f"DEBUG: ABSOLUTE metadata_path: {abs_path}", flush=True)
        temp_df = pd.read_csv(abs_path)
        print(f"DEBUG: metadata.csv shape after load: {temp_df.shape}", flush=True)
        print(f"DEBUG: metadata.csv head after load:\n{temp_df.head(10)}", flush=True)
        st.session_state['metadata'] = temp_df
        print(f"DEBUG: metadata DataFrame head after session_state assign:\n{st.session_state['metadata'].head(10)}", flush=True)

        # DEBUG: Always extract salaries and print for debugging
        salaries = []
        if 'text' in temp_df.columns:
            for row in temp_df.itertuples():
                text_str = str(row.text) if not isinstance(row.text, str) else row.text
                match = re.search(r'Name:\s*([^|]+)\s*\|\s*Department:\s*([^|]+)(?:\s*\|\s*Title:\s*([^|]+))?\s*\|\s*Salary:\s*\$([\d,]+)', text_str)
                if match:
                    name = match.group(1).strip()
                    dept = match.group(2).strip()
                    title = match.group(3).strip() if match.group(3) else ''
                    salary = match.group(4).strip()
                    salaries.append((name, title, dept, salary))
        print(f"DEBUG: salaries extracted (unconditional): {salaries}", flush=True)
    elif os.path.exists(chunks_path):
        print(f"DEBUG: metadata_path missing, loading chunks_path: {chunks_path}", flush=True)
        st.session_state['metadata'] = pd.read_csv(chunks_path)
    else:
        print(f"DEBUG: neither metadata_path nor chunks_path found, using empty DataFrame", flush=True)
        st.session_state['metadata'] = pd.DataFrame()
    # Assign metadata from session state
    metadata = st.session_state['metadata']

# --- LLM Model Selection and Display ---
# Define available LLM model options
GEN_MODEL_OPTIONS = [
    'Ollama (llama2:7b-chat)',
    'Ollama (mistral:7b-instruct)',
    'Ollama (phi3:mini)',
    'gpt2',
    'distilgpt2',
    # Add more model names as needed
]

col1, col2 = st.columns([1,1], gap="large")
with col1:
    st.markdown('<span class="dropdown-label-align">LLM Model:</span>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "LLM Model",
        GEN_MODEL_OPTIONS,
        index=GEN_MODEL_OPTIONS.index('Ollama (llama2:7b-chat)'),
        key="llm_model_select",
        label_visibility="collapsed"
    )
with col2:
    st.markdown('<span class="dropdown-label-align">Role:</span>', unsafe_allow_html=True)
    current_role = st.session_state.get('user_role', ROLES[0])
    new_role = st.selectbox(
        "Role",
        ROLES,
        index=ROLES.index(current_role) if current_role in ROLES else 0,
        key="role_switch_select",
        label_visibility="collapsed",
        format_func=lambda r: f"{r} - {ROLE_DESCRIPTIONS[r]}"
    )
    if new_role != current_role:
        st.session_state['user_role'] = new_role
        st.rerun()


# Map dropdown display names to valid HuggingFace model names
MODEL_NAME_MAP = {
    'Ollama (llama2:7b-chat)': 'ollama',
    'Ollama (mistral:7b-instruct)': 'ollama',
    'Ollama (phi3:mini)': 'ollama',
    'gpt2': 'gpt2',
    'distilgpt2': 'distilgpt2',
}

# When the user changes the model in the dropdown, reload the pipeline and update session state
model_name = MODEL_NAME_MAP.get(selected_model, 'gpt2')
if 'selected_model' not in st.session_state or st.session_state['selected_model'] != selected_model or st.session_state.get('last_model_name') != model_name:
    st.session_state['selected_model'] = selected_model
    st.session_state['llm'], st.session_state['gen_model_display'] = load_llm_pipeline(model_name)
    st.session_state['last_model_name'] = model_name

def retrieve(query, top_k=3):
    # Placeholder for retrieve logic. Actual logic moved to backend or needs to be re-implemented.
    st.warning('Retrieve logic is not implemented. Please update this section.')
    return pd.DataFrame()
    query_emb = embed_model.encode([query]).astype('float32')
    if len(query_emb.shape) == 1:
        query_emb = query_emb.reshape(1, -1)
    top_k = 5  # Retrieve more chunks for richer answers
    # Ensure query_emb is contiguous float32 (n, d)
    if not query_emb.flags['C_CONTIGUOUS']:
        query_emb = np.ascontiguousarray(query_emb, dtype='float32')
    if query_emb.ndim != 2:
        raise ValueError(f"query_emb must be 2D (n, d), got shape {query_emb.shape}")
    try:
        if hasattr(index, 'search') and index.ntotal > 0:
            D, I = index.search(query_emb, top_k)
        else:
            D, I = np.array([]), np.array([])
    except Exception as e:
        D, I = np.array([]), np.array([])
    # Defensive: I is a 2D numpy array (n_queries, top_k)
    if hasattr(I, '__getitem__') and len(I) > 0 and hasattr(I[0], '__iter__'):
        idxs = [i for i in I[0] if i >= 0]
        results = metadata.iloc[idxs] if len(idxs) > 0 else pd.DataFrame()
    else:
        results = pd.DataFrame()
    # If the query is about deployment, always include the deploy_software_sop chunk
    if 'deploy' in query.lower() or 'deployment' in query.lower():
        sop_mask = metadata['file'].astype(str).str.contains('deploy_software_sop', case=False, na=False)
        sop_chunk = metadata[sop_mask]
        if not sop_chunk.empty:
            if 'file' in results.columns:
                in_results = results['file'].astype(str).str.contains('deploy_software_sop', case=False, na=False)
                if not in_results.any():
                    results = pd.concat([results, sop_chunk], ignore_index=True)
            elif not results.empty:
                results = pd.concat([results, sop_chunk], ignore_index=True)
            else:
                results = sop_chunk.copy()

    # If the query is about PTO/vacation, always include the vacation_policy chunk
    pto_keywords = ['pto', 'paid time off', 'vacation', 'leave', 'holiday']
    if any(kw in query.lower() for kw in pto_keywords):
        vac_mask = metadata['file'].astype(str).str.contains('vacation_policy', case=False, na=False)
        vac_chunk = metadata[vac_mask]
        if not vac_chunk.empty:
            if 'file' in results.columns:
                in_results = results['file'].astype(str).str.contains('vacation_policy', case=False, na=False)
                if not in_results.any():
                    results = pd.concat([results, vac_chunk], ignore_index=True)
            elif not results.empty:
                results = pd.concat([results, vac_chunk], ignore_index=True)
            else:
                results = vac_chunk.copy()
    # RBAC: Filter Technology department salary data for non-CTO roles
    user_role = st.session_state.get('user_role', None)
    if user_role != 'CTO' and 'salary' in query.lower():
        # Remove Technology department salary chunks
        if not results.empty and 'text' in results.columns:
            mask = ~results['text'].astype(str).str.contains('Department: Technology', case=False, na=False)
            results = results[mask]
    return results

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Patch old chat history in memory to always include LLM name if missing or set to 'neutral'


# CSS for scrollable chat box and chat bubbles
st.markdown('''
<style>
.scrollable-chat-window {
    width: 100%;
    margin: 0;
    height: 420px;
    min-height: 220px;
    max-height: 60vh;
    overflow-y: scroll;
    padding: 0 2px 0 2px;
    background: #fafbfc;
    border: 1px solid #eee;
    border-radius: 8px;
    display: flex;
    flex-direction: column-reverse;
    scrollbar-color: #bbb #fafbfc;
    scrollbar-width: thin;
}
.chat-bubble-user {
    background: #d1e7ff;
    color: #222;
    padding: 6px 10px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 2px;
    max-width: 70%;
    align-self: flex-end;
    margin-right: 0;
    margin-left: 30%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    font-weight: 500;
}
.chat-bubble-bot {
    background: #f0f0f0;
    color: #222;
    padding: 6px 10px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 6px;
    max-width: 70%;
    align-self: flex-end;
    margin-right: 0;
    margin-left: 30%;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.scrollable-chat-window::-webkit-scrollbar {
    width: 8px;
}
.scrollable-chat-window::-webkit-scrollbar-thumb {
    background: #bbb;
    border-radius: 4px;
}
.scrollable-chat-window::-webkit-scrollbar-track {
    background: #fafbfc;
}
.input-bar {
    width: 100%;
    margin: 0;
    background: #fff;
    padding: 0 0 2px 0;
}
@media (max-width: 900px) {
    .scrollable-chat-window {
        height: 220px;
        min-height: 120px;
        max-height: 32vh;
    }
}
</style>
''', unsafe_allow_html=True)


# Scrollable chat window with fixed height, messages start at bottom
 # Scrollable chat window with fixed height, messages start at bottom

# Render messages in normal order (newest at bottom) with feedback



import uuid
            # ...existing code...
            # Ensure provenance is always set for all salary queries, including fallback and direct lookups
chat_html = '<div class="scrollable-chat-window">'

# --- Enhanced: Display source files for each answer ---
for idx, entry in enumerate(reversed(st.session_state.get('history', []))):
    # Unpack entry

    # Always store the selected model at the time of response
    # Robustly unpack all possible formats (7, 6, 5, 4, 3, 2 fields)
    user = bot = response_time = llm_used = sources = model_used = user_role_at_time = None
    if len(entry) == 7:
        user, bot, response_time, llm_used, sources, model_used, user_role_at_time = entry
    elif len(entry) == 6:
        user, bot, response_time, llm_used, sources, user_role_at_time = entry
        model_used = llm_used
    elif len(entry) == 5:
        user, bot, response_time, llm_used, user_role_at_time = entry
        sources = None
        model_used = llm_used
    elif len(entry) == 4:
        user, bot, response_time, llm_used = entry
        sources = None
        model_used = llm_used
        user_role_at_time = None
    elif len(entry) == 3:
        user, bot, response_time = entry
        llm_used = ''
        sources = None
        model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
        user_role_at_time = None
    elif len(entry) == 2:
        user, bot = entry
        response_time = None
        llm_used = ''
        sources = None
        model_used = st.session_state.get('selected_model') or GEN_MODEL_NAME
        user_role_at_time = None

    # Always show response time and LLM model at the bottom of the bot message
    # Always display the model actually used for this response
    llm_display = f' | {model_used}'
    time_llm_html = f'<span style="font-size:0.85em;color:#888;">{llm_display}</span>'
    chat_html += f'<div>'
    # Role-specific icon and label for user chat bubble
    role_icons = {
        'Alice Johnson (HR)': '🧑‍💼',
        'David Kim (Engineer)': '🧑‍💻',
        'Olivia Zhang (CTO)': '🧑‍💼',
    }
    role_labels = {
        'Alice Johnson (HR)': 'Alice Johnson (HR)',
        'David Kim (Engineer)': 'David Kim (Engineer)',
        'Olivia Zhang (CTO)': 'Olivia Zhang (CTO)',
    }
    # Normalize CTO and HR role to always display as their full label
    if user_role_at_time == 'CTO' or user_role_at_time == 'Olivia Zhang (CTO)':
        display_role = 'Olivia Zhang (CTO)'
    elif user_role_at_time == 'HR' or user_role_at_time == 'Alice Johnson (HR)':
        display_role = 'Alice Johnson (HR)'
    elif user_role_at_time == 'David Kim (Engineer)':
        display_role = 'David Kim (Engineer)'
    else:
        display_role = user_role_at_time or 'You'
    icon = role_icons.get(display_role, '🧑')
    label = role_labels.get(display_role, display_role)
    chat_html += f'<div class="chat-bubble-user">{icon} <b>{label}:</b> {user}</div>'
    chat_html += f'<div class="chat-bubble-bot">&#129302; <b>Chatbot:</b> {bot}'
    # Show source file for onboarding answers
    # Only show sources if not None, not empty, and not a denial/warning message
    if sources and sources not in [None, '', [], 'None'] and not (isinstance(bot, str) and 'Unauthorized access attempt' in bot):
        def file_to_link(file):
            try:
                rel_path = os.path.relpath(str(file), os.path.dirname(__file__))
                rel_path_url = rel_path.replace('\\', '/').replace(' ', '%20')
                if rel_path_url.startswith(('mock_data/', 'ingestion/', 'vector_db/')):
                    return f'<a href="/{rel_path_url}" target="_blank">{os.path.basename(str(file))}</a>'
                else:
                    return os.path.basename(str(file))
            except Exception:
                return os.path.basename(str(file))
        if isinstance(sources, list) and sources:
            src_links = ', '.join([file_to_link(s) for s in sources])
            src_html = f'<br><span style="font-size:0.85em;color:#1976d2;">Sources: {src_links}</span>'
            chat_html += src_html
        elif isinstance(sources, str) and sources:
            chat_html += f'<br><span style="font-size:0.85em;color:#1976d2;">Source: {file_to_link(sources)}</span>'
    # Only show LLM model used, not response time
    if time_llm_html:
        chat_html += f'<br><span style="display:block;text-align:right;margin-top:4px;font-size:0.95em;color:#555;">{time_llm_html}</span>'
    chat_html += '</div>'
    chat_html += f'</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Inject scroll-to-bottom script separately and persistently
st.markdown('''
<script>
    function scrollChatToBottom() {
        const chatWin = document.querySelector('.scrollable-chat-window');
        if (chatWin) {
            chatWin.scrollTop = chatWin.scrollHeight;
        }
    }
    // Try repeatedly for 1s after each render
    let scrollTries = 0;
    const maxTries = 20;
    const interval = setInterval(() => {
        scrollChatToBottom();
        scrollTries++;
        if (scrollTries > maxTries) clearInterval(interval);
    }, 50);
    // Also scroll on window load
    window.addEventListener('load', scrollChatToBottom);
</script>
''', unsafe_allow_html=True)

# Input bar just below chat window
st.markdown('<div class="input-bar">', unsafe_allow_html=True)
with st.form(key='chat_input_form', clear_on_submit=True):
    user_input = st.text_input("Message", "", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        user_role = st.session_state.get('user_role', 'You')
        metadata = st.session_state.get('metadata', pd.DataFrame())
        bot_response = ''
        provenance = None
        model_used = st.session_state.get('selected_model', GEN_MODEL_NAME)
        response_time = None
        # Engineer RBAC logic
        if user_role == 'David Kim (Engineer)':
            from llm_backend.rbac_service import check_engineer_salary_access
            result = check_engineer_salary_access(user_role, user_input, metadata, fuzzy_any)
            if result.get('denied'):
                bot_response = result.get('message', 'Access denied.')
            elif result.get('salary_row') is not None:
                df = result['salary_row']
                bot_response = df.to_html(index=False, escape=False, border=0, classes="salary-table")
                provenance = 'payroll_confidential.txt'
            else:
                bot_response = 'No salary information found.'
        # HR/CTO logic
        elif user_role in ['Alice Johnson (HR)', 'Olivia Zhang (CTO)']:
            from llm_backend.salary_service import get_salary_and_provenance
            # Extract salaries from metadata
            salaries = []
            if isinstance(metadata, pd.DataFrame) and 'text' in metadata.columns:
                for row in metadata.itertuples():
                    text_str = str(row.text) if not isinstance(row.text, str) else row.text
                    match = re.search(r'Name:\s*([^|]+)\s*\|\s*Department:\s*([^|]+)(?:\s*\|\s*Title:\s*([^|]+))?\s*\|\s*Salary:\s*\$([\d,]+)', text_str)
                    if match:
                        name = match.group(1).strip()
                        dept = match.group(2).strip()
                        title = match.group(3).strip() if match.group(3) else ''
                        salary = match.group(4).strip()
                        salaries.append((name, title, dept, salary))
            result = get_salary_and_provenance(user_role, user_input, salaries, fuzzy_any)
            if 'html_table' in result:
                bot_response = result['html_table']
            elif 'message' in result:
                bot_response = result['message']
            provenance = result.get('provenance')
        else:
            bot_response = "I'm sorry, I can't answer that."
        # Append to chat history
        st.session_state.setdefault('history', []).append((user_input, bot_response, response_time, model_used, provenance, model_used, user_role))
        st.rerun()
        # Placeholder for model_used and response_time to avoid NameError
        llm_display = f' | ' + str(st.session_state.get('selected_model', 'Unknown'))
        response_time = None
        time_llm_html = ''
        # chat_html += f'<div>'
        # Role-specific icon and label for user chat bubble
        role_icons = {
            'HR': '🧑‍💼',
            'Engineering': '🧑‍💻',
            'David Kim (Engineer)': '🧑‍💻',
            'CTO': '🧑‍💼',
        }
        role_labels = {
            'HR': 'HR',
            'Engineering': 'Engineering',
            'David Kim (Engineer)': 'David Kim (Engineer)',
            'CTO': 'CTO',
        }
        # Placeholder for user_role_at_time to avoid NameError
        display_role = 'You'
        icon = role_icons.get(display_role, '🧑')
        label = role_labels.get(display_role, display_role)
        # chat_html += f'<div class="chat-bubble-user">{icon} <b>{label}:</b> {user}</div>'
        # chat_html += f'<div class="chat-bubble-bot">&#129302; <b>Bot:</b> {bot}'
        # Show source file for onboarding answers
        # Only show sources if not None, not empty, and not a denial/warning message
        sources = None  # Placeholder to avoid NameError
        if sources and sources not in [None, '', [], 'None']:
            def file_to_link(file):
                try:
                    rel_path = os.path.relpath(str(file), os.path.dirname(__file__))
                    rel_path_url = rel_path.replace('\\', '/').replace(' ', '%20')
                    if rel_path_url.startswith(('mock_data/', 'ingestion/', 'vector_db/')):
                        return f'<a href="/{rel_path_url}" target="_blank">{os.path.basename(str(file))}</a>'
                    else:
                        return os.path.basename(str(file))
                except Exception:
                    return os.path.basename(str(file))
            if isinstance(sources, list) and sources:
                src_links = ', '.join([file_to_link(s) for s in sources])
                src_html = f'<br><span style="font-size:0.85em;color:#1976d2;">Sources: {src_links}</span>'
                chat_html += src_html
            elif isinstance(sources, str) and sources:
                chat_html += f'<br><span style="font-size:0.85em;color:#1976d2;">Source: {file_to_link(sources)}</span>'
st.markdown('</div>', unsafe_allow_html=True)




if not ECHO_MODE:
    # Streamlit UI

    # Track model type for logging (dynamic)

    # Collapsible sidebar sections (default collapsed)
    st.sidebar.markdown("""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
    <span style='font-size:1.08em;font-weight:600;color:#1976d2;'>&#128241; App version:</span><br>
    <span style='font-size:1.05em;color:#222;'>v1.0.3 - Enterprise RBAC, Role-Preserved Chat, Modern UI</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style="font-size:1.05em;vertical-align:middle;">&#129302;</span> AI Search & Knowledge System
    </div>
    <div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128269;</span> <span>Semantic Search (FAISS + SentenceTransformers)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128196;</span> <span>Document Q&amp;A (PDF, DOCX, TXT)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128273;</span> <span>Enterprise RBAC & Audit Logging</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128187;</span> <span>Modern, Unified Chat UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128221;</span> <span>Role-Preserved Chat History</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128202;</span> <span>Feedback, Metrics, and Logging</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128640;</span> <span>LLM: Ollama & HuggingFace</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128736;</span> <span>Fully Tested (pytest)</span>
        </div>
    </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128737;</span> <span>Private, Local LLM</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#9889;</span> <span>Fast, Modern UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128274;</span> <span>Role-Based Access Control (RBAC)</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">&#128100;</span> <span>Role-Preserved Chat History</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;'>
            <span style="font-size:1em;">&#128202;</span> <span>Feedback Logging</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Restore About This Project expander at the top
    with st.sidebar.expander("ℹ️ About This Project", expanded=False):
        st.markdown("""
        Portfolio Project
        - Secure, local AI chatbot for enterprise document Q&A
        - Strict role-based access control (RBAC) for sensitive data
        - Real-time semantic search and retrieval
        - Unified, modern chat UI with persistent role/model display
        - Modular, extensible Python/Streamlit codebase
        - Production-grade deployment and reproducible environments
        - Robust feedback logging and evaluation

        **Target Audience:**
        Technology executives, engineering leaders, HR professionals, AI/ML practitioners, and technical decision-makers interested in secure document Q&A, RBAC enforcement, and advanced LLM-driven systems for enterprise use cases.

        **What This Demonstrates:**
        - Deep LLM integration (Ollama, HuggingFace Transformers)
        - Multi-role RBAC enforcement and salary logic
        - Unified, modern chat UI with persistent role/model display
        - Clean architecture, modular code, and documentation
        - Technical leadership and system design for enterprise AI
    """, unsafe_allow_html=True)
        with st.sidebar.expander("&#128193; Project Documentation", expanded=False):
            st.markdown("**Project Documentation**")
            st.markdown("[GitHub Repository](https://github.com/obizues/Local-AI-Chatbot-POC)")
            st.markdown("**Documentation**")
            st.markdown("- [README.md](https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/README.md): Project overview, quick start, features")
            st.markdown("- [ARCHITECTURE.md](https://github.com/obizues/Local-AI-Chatbot-POC/blob/main/ARCHITECTURE.md): Deep technical documentation")
            st.markdown("- System Diagrams: 5 Mermaid diagrams")
            st.markdown("**Key Sections:**\n- Multi-agent system design\n- LLM integration strategy\n- Production deployment guide\n- Architectural decision records")
    with st.sidebar.expander("&#128295; Tech Stack", expanded=False):
        st.markdown("""
    <span style='font-size:1em;'>
    <ul style='margin-bottom:0; padding-left: 18px;'>
    <li>Python 3.10+</li>
    <li>Streamlit (UI)</li>
    <li>FAISS (vector search)</li>
    <li>sentence-transformers (embeddings)</li>
    <li>HuggingFace Transformers (LLM pipeline)</li>
    <li>Ollama (local LLM, optional)</li>
    <li>Flask (API integration)</li>
    <li>pandas (data handling)</li>
    <li>NumPy (vector math)</li>
    <li>PyMuPDF (PDF ingestion)</li>
    <li>python-docx (DOCX ingestion)</li>
    <li>langchain, llama-index (optional, advanced retrieval)</li>
    </ul>
    </span>
    """, unsafe_allow_html=True)
st.markdown("""
<div style='font-size:1.12em;font-weight:700;margin-bottom:8px;'>System Design Notes</div>
<ul style='margin-bottom:0; padding-left: 18px;'>
    <li><b>Retrieval-Augmented Chat:</b> User questions are embedded and matched to relevant document chunks using FAISS, providing context for LLM answers.</li>
    <li><b>Unified Chat Interface:</b> Streamlit UI displays chat history, model selection, and sidebar documentation in a single, modern layout.</li>
    <li><b>Session State Management:</b> All chat history, selected model, and user context are stored in Streamlit session state for seamless multi-turn conversations.</li>
    <li><b>Flexible LLM Backend:</b> Supports both local (Ollama) and HuggingFace LLMs, switchable via UI, with fallback and error handling for robustness.</li>
    <li><b>Document Ingestion Pipeline:</b> Batch scripts process PDFs, DOCX, and text files, chunking and embedding them for fast semantic search.</li>
    <li><b>Feedback Logging:</b> User queries, responses, and feedback are logged to CSV for evaluation and improvement.</li>
    <li><b>Customizable Sidebar:</b> Sidebar provides About, Documentation, Tech Stack, and System Design Notes, all styled for clarity and mobile compatibility.</li>
    <li><b>Real-Time UI Updates:</b> Chat and sidebar update instantly on user input, with scroll-to-bottom and feedback features for usability.</li>
    <li><b>Extensible Architecture:</b> Modular codebase allows easy addition of new models, data sources, or UI features.</li>
    <li><b>Observability:</b> Debug logs and error messages are written to local files for troubleshooting and transparency.</li>
    <li><b>Resilience:</b> Graceful error handling ensures the app remains usable even if some components fail or are unavailable.</li>
    <li><b>Infrastructure:</b> Designed for local use, but can be containerized or deployed on private servers as needed.</li>
</ul>
""", unsafe_allow_html=True)
st.markdown("**Security & Privacy:** All processing is local; no data leaves the user's environment. API keys and secrets are managed via environment variables and never committed to source control.", unsafe_allow_html=True)