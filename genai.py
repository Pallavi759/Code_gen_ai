import streamlit as st
from groq import Groq
import speech_recognition as sr
from PIL import Image
import pytesseract
import os
import sys
import uuid
from datetime import datetime

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# OCR Setup
try:
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
    if sys.platform.startswith('win'):
        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
except:
    OCR_AVAILABLE = False

st.set_page_config(
    page_title="Code Gen AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state=st.session_state.get("sidebar_state", "expanded"),
)

# UPDATED CSS - File/speech buttons same class, welcome buttons rectangular
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
    padding-bottom: 80px;
}

/* Ensure sidebar toggle arrow is always visible and on top */
div[data-testid="collapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 3000 !important;
}

/* Chat input container stays white / light */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 300px;
    right: 0;
    padding: 1rem 2rem;
    background: #ffffff !important;
    backdrop-filter: blur(20px);
    border-top: 1px solid #e5e7eb;
    z-index: 1000;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
}

/* Outer text input wrapper */
[data-testid="stTextInput"] > div > div > div {
    background: #ffffff !important;
    border-radius: 24px !important;
    border: 2px solid #e5e7eb !important;
    padding: 0.5rem 1.25rem !important;
    height: 48px !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

/* Actual text field */
[data-testid="stTextInput"] input {
    color: #111827 !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
    height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
    caret-color: #3b82f6 !important;
    -webkit-appearance: none !important;
}

/* Placeholder text */
[data-testid="stTextInput"] input::placeholder {
    color: #9ca3af !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.95) !important;
    backdrop-filter: none !important;
    width: 300px !important;
    padding: 1rem !important;
    box-shadow: none !important;
    border-right: 1px solid #e5e7eb !important;
}

.sidebar-header {
    padding: 1.5rem 1.5rem !important;
    margin: -1rem -1rem 1.5rem -1rem !important;
    background: linear-gradient(135deg, #000000, #333333) !important;
    border-radius: 12px !important;
    text-align: center !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}

.sidebar-title {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: white !important;
    margin: 0 !important;
}

.sidebar-subtitle {
    font-size: 0.85rem !important;
    color: rgba(255,255,255,0.9) !important;
    margin-top: 0.25rem !important;
}

.new-chat-btn {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.25rem !important;
    margin-bottom: 1rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 12px rgba(16,185,129,0.3) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.new-chat-btn:hover {
    background: linear-gradient(135deg, #059669, #047857) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(16,185,129,0.4) !important;
}

.sidebar-section-title {
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin: 1.5rem 0 0.75rem 0 !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 1px solid #e5e7eb !important;
}

/* HIDE DEFAULT ELEMENTS */
header[data-testid="stHeader"], footer { display: none !important; }

/* PERFECT WELCOME */
.welcome-container {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    padding: 3rem 2.5rem;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    margin: 2rem 0;
}

.welcome-title {
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: #1f2937 !important;
    margin-bottom: 1rem !important;
}

.welcome-subtitle {
    font-size: 1.15rem !important;
    color: #374151 !important;
    line-height: 1.7 !important;
    margin-bottom: 2.5rem !important;
}

/* RECTANGULAR WELCOME BUTTONS */
div[data-testid="column"] button[kind="primary"][key*="trigger"],
button.welcome-btn {
    background: linear-gradient(135deg, #000000, #333333) !important;
    color: white !important;
    border: 2px solid #444444 !important;
    border-radius: 12px !important;
    padding: 1.2rem 2.5rem !important;
    margin: 0.5rem !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
    width: 260px !important;
    height: 70px !important;
    line-height: 1.2 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="column"] button[kind="primary"][key*="trigger"]:hover,
button.welcome-btn:hover {
    background: linear-gradient(135deg, #333333, #555555) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
    border-color: #666666 !important;
}

/* GENERAL BUTTON STYLES */
[data-testid="stButton"] > button:not([key*="trigger"]):not([key*="explain_btn"]):not([key*="code_btn"]):not([key*="ideas_btn"]) {
    background: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 0.875rem 1rem !important;
    margin-bottom: 0.5rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    width: 100% !important;
}

[data-testid="stButton"] > button:not([key*="trigger"]):not([key*="explain_btn"]):not([key*="code_btn"]):not([key*="ideas_btn"]):hover {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
    border-color: #3b82f6 !important;
    color: #1f2937 !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.15) !important;
}

/* CHROME-PERFECT TEXT INPUT */
.chat-input-container {
    position: fixed;
    bottom: 0;
    left: 300px;
    right: 0;
    padding: 1rem 2rem;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(20px);
    border-top: 1px solid #e5e7eb;
    z-index: 1000;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
}

.chat-input-row {
    display: flex;
    align-items: center;
    gap: 6px;
    max-width: 1200px;
    margin: 0 auto;
    height: 48px;
}

[data-testid="stTextInput"] {
    width: 100% !important;
}

[data-testid="stTextInput"] > div > div > div {
    background: #ffffff !important;
    border-radius: 24px !important;
    border: 2px solid #e5e7eb !important;
    padding: 0.5rem 1.25rem !important;
    height: 48px !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    border: none !important;
}

[data-testid="stTextInput"]:hover > div > div > div {
    border-color: #3b82f6 !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.15) !important;
}

[data-testid="stTextInput"]:focus-within > div > div > div {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1), 0 2px 12px rgba(59,130,246,0.15) !important;
}

[data-testid="stTextInput"] input {
    color: #1f2937 !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
    height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
    caret-color: #3b82f6 !important;
    -webkit-appearance: none !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #9ca3af !important;
}

/* UPDATED BUTTON STYLES - File & Speech same class .action-btn */
.attach-btn, .mic-btn, .action-btn {
    height: 48px !important;
    width: 48px !important;
    border-radius: 24px !important;
    border: none !important;
    font-size: 1.2rem !important;
    color: white !important;
    flex-shrink: 0;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin: 0 !important;
    -webkit-appearance: none !important;
}

.attach-btn {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    box-shadow: 0 2px 8px rgba(16,185,129,0.3) !important;
}

.attach-btn:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.4) !important;
}

.mic-btn, .action-btn {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    box-shadow: 0 2px 8px rgba(239,68,68,0.3) !important;
}

.mic-btn:hover, .action-btn:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 16px rgba(239,68,68,0.4) !important;
}

[data-testid="column"] {
    padding: 0 2px !important;
    margin: 0 !important;
}

.chat-message {
    display: flex;
    margin: 1rem 0;
}

.user-message { justify-content: flex-end; padding-right: 1rem; }
.assistant-message { padding-left: 1rem; }

.message-bubble {
    max-width: 60%;
    padding: 1rem 1.25rem;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-size: 15px;
    line-height: 1.5;
    color: #1f2937 !important;
}

.user-bubble {
    background: white;
    border-radius: 20px 20px 6px 20px;
}

.assistant-bubble {
    background: rgba(255,255,255,0.8);
    border-radius: 20px 20px 20px 6px;
    backdrop-filter: blur(10px);
}

.message-timestamp {
    font-size: 0.75rem !important;
    color: #9ca3af !important;
    margin-top: 0.5rem !important;
    font-weight: 400 !important;
}

::-webkit-scrollbar { 
    width: 8px; 
    height: 8px;
}
::-webkit-scrollbar-track { 
    background: rgba(0,0,0,0.05); 
    border-radius: 4px;
}
::-webkit-scrollbar-thumb { 
    background: rgba(0,0,0,0.2); 
    border-radius: 4px; 
}
::-webkit-scrollbar-thumb:hover { 
    background: rgba(0,0,0,0.3); 
}

.logo-container {
    width: 120px;
    height: 120px;
    background: linear-gradient(135deg, #000000, #333333);
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 56px;
    margin: 0 auto 1.4rem;
    box-shadow: 0 18px 32px rgba(0,0,0,0.3);
    animation: float 6s ease-in-out infinite;
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
    100% { transform: translateY(0px); }
}

button[kind="primary"][key="explain_btn"]:hover,
button[kind="primary"][key="code_btn"]:hover,
button[kind="primary"][key="ideas_btn"]:hover {
    background: linear-gradient(135deg, #333333, #555555) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
    border-color: #666666 !important;
}
</style>
""", unsafe_allow_html=True)

GROQ_API_KEY = "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"

# Session state
if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = []
if "active_thread_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chat_threads.append({"id": new_id, "title": "New Chat", "messages": []})
    st.session_state.active_thread_id = new_id
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = None
if "show_file_uploader" not in st.session_state:
    st.session_state.show_file_uploader = False
if "last_input_length" not in st.session_state:
    st.session_state.last_input_length = {}
if "welcome_action" not in st.session_state:
    st.session_state.welcome_action = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama-3.1-8b-instant"

# Welcome button callbacks
def explain_callback():
    st.session_state.welcome_action = "explain"

def code_callback():
    st.session_state.welcome_action = "code"

def ideas_callback():
    st.session_state.welcome_action = "ideas"

# All functions
def call_groq(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    model = st.session_state.get("selected_model", "llama-3.1-8b-instant")

    system_message = {
        "role": "system",
        "content": (
            "You are a senior software engineer and code fixer.\n"
            "Your job:\n"
            "- Read the code or error the user gives.\n"
            "- Identify bugs, bad practices, and potential issues.\n"
            "- Return improved, corrected code with clear explanations.\n"
            "- Keep answers focused on code, debugging, and best practices."
        )
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except:
        return "Sorry, I'm having trouble right now."

def speech_to_text():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return r.recognize_google(audio)
    except:
        return None

def process_ocr(file):
    try:
        if file.type.startswith('image/'):
            img = Image.open(file)
            return pytesseract.image_to_string(img)
        elif 'pdf' in file.type.lower() and OCR_AVAILABLE:
            pages = convert_from_bytes(file.read())
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page) + "\\n"
            return text
        else:
            return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"OCR failed: {str(e)}")
        return None

def get_active_thread():
    for thread in st.session_state.chat_threads:
        if thread["id"] == st.session_state.active_thread_id:
            return thread
    if st.session_state.chat_threads:
        return st.session_state.chat_threads[0]
    return None

def create_new_chat():
    new_id = str(uuid.uuid4())
    new_thread = {"id": new_id, "title": "New Chat", "messages": []}
    st.session_state.chat_threads.insert(0, new_thread)
    st.session_state.active_thread_id = new_id
    st.session_state.ocr_text = None
    st.session_state.show_file_uploader = False
    st.session_state.last_input_length = {}
    st.session_state.welcome_action = None
    st.rerun()

def update_thread_title(thread_id, new_title):
    for thread in st.session_state.chat_threads:
        if thread["id"] == thread_id:
            thread["title"] = new_title[:30] + "..." if len(new_title) > 30 else new_title
            break

def quick_action_prompt(action_type):
    prompts = {
        "explain": (
            "Act as a code fixer. Explain this programming concept clearly with examples, "
            "and show how to debug typical mistakes."
        ),
        "code": (
            "Act as a code fixer. Write clean, working code for the described task and "
            "explain any important implementation details and edge cases."
        ),
        "ideas": (
            "Act as a senior engineer. Propose project ideas that involve writing and improving code, "
            "and briefly outline how the code structure should look."
        )
    }
    return prompts.get(action_type, "")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-title">🤖 Code Gen AI</div>
        <div class="sidebar-subtitle">Your coding companion</div>
    </div>
    """, unsafe_allow_html=True)

    # Model selection
    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768"
    ]
    model = st.selectbox(
        "Model",
        model_options,
        index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
        key="model_select",
    )
    st.session_state.selected_model = model

    # New Chat button
    if st.button("➕ New Chat", key="new_chat_perfect", use_container_width=True):
        create_new_chat()

    # Delete all chats button
    if st.button("🗑️ Delete all chats", key="delete_all_chats", use_container_width=True):
        st.session_state.chat_threads = []
        new_id = str(uuid.uuid4())
        st.session_state.chat_threads.append(
            {"id": new_id, "title": "New Chat", "messages": []}
        )
        st.session_state.active_thread_id = new_id
        st.session_state.ocr_text = None
        st.session_state.show_file_uploader = False
        st.session_state.last_input_length = {}
        st.session_state.welcome_action = None
        st.rerun()

    st.markdown('<div class="sidebar-section-title">Recent Chats</div>', unsafe_allow_html=True)

    # Search chats
    search_query = st.text_input(
        "Search chats",
        value="",
        key="search_chats",
        label_visibility="collapsed",
        placeholder="Search chats..."
    )

    # Filter threads
    filtered_threads = []
    for thread in st.session_state.chat_threads:
        title = thread["title"].lower()
        first_msg = thread["messages"][0]["content"].lower() if thread["messages"] else ""
        if search_query.lower() in title or search_query.lower() in first_msg:
            filtered_threads.append(thread)

    # Show up to last 8 filtered threads
    for thread in filtered_threads[-8:]:
        thread_title = thread["title"]
        if thread["messages"]:
            thread_title = f"💬 {thread['messages'][0]['content'][:25]}..."
        if st.button(thread_title, key=f"thread_{thread['id']}", use_container_width=True):
            st.session_state.active_thread_id = thread["id"]
            st.rerun()

# MAIN CONTENT
active_thread = get_active_thread()
if active_thread is None:
    st.error("No active chat found. Create a new chat.")
    st.stop()

st.session_state.messages = active_thread["messages"].copy()

if not st.session_state.messages:
    # Welcome screen with proper Streamlit buttons
    st.markdown("""
    <div class="welcome-container">
        <div class="logo-container">💻</div>
        <div class="welcome-title">Welcome to Code-Geni AI</div>
        <div class="welcome-subtitle">
            Illuminate your conversations with AI-powered assistance. Upload images, ask questions, and enjoy intelligent responses.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📚 Explain a concept", key="explain_btn", use_container_width=True):
            st.session_state.welcome_action = "explain"
            st.rerun()

    with col2:
        if st.button("💻 Write code", key="code_btn", use_container_width=True):
            st.session_state.welcome_action = "code"
            st.rerun()

    with col3:
        if st.button("💡 Get ideas", key="ideas_btn", use_container_width=True):
            st.session_state.welcome_action = "ideas"
            st.rerun()

    if st.session_state.welcome_action == "explain":
        quick_prompt = quick_action_prompt("explain")
        timestamp = datetime.now().strftime("%H:%M")
        user_content = "📚 Explain a concept"
        st.session_state.messages.append({"role": "user", "content": user_content, "timestamp": timestamp})
        active_thread["messages"].append({"role": "user", "content": user_content, "timestamp": timestamp})
        update_thread_title(st.session_state.active_thread_id, user_content)

        with st.spinner("🤖 Thinking..."):
            response = call_groq(quick_prompt)
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            active_thread["messages"].append({"role": "assistant", "content": response, "timestamp": timestamp})

        st.session_state.welcome_action = None
        st.rerun()

    elif st.session_state.welcome_action == "code":
        quick_prompt = quick_action_prompt("code")
        timestamp = datetime.now().strftime("%H:%M")
        user_content = "💻 Write code"
        st.session_state.messages.append({"role": "user", "content": user_content, "timestamp": timestamp})
        active_thread["messages"].append({"role": "user", "content": user_content, "timestamp": timestamp})
        update_thread_title(st.session_state.active_thread_id, user_content)

        with st.spinner("🤖 Thinking..."):
            response = call_groq(quick_prompt)
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            active_thread["messages"].append({"role": "assistant", "content": response, "timestamp": timestamp})

        st.session_state.welcome_action = None
        st.rerun()

    elif st.session_state.welcome_action == "ideas":
        quick_prompt = quick_action_prompt("ideas")
        timestamp = datetime.now().strftime("%H:%M")
        user_content = "💡 Get ideas"
        st.session_state.messages.append({"role": "user", "content": user_content, "timestamp": timestamp})
        active_thread["messages"].append({"role": "user", "content": user_content, "timestamp": timestamp})
        update_thread_title(st.session_state.active_thread_id, user_content)

        with st.spinner("🤖 Thinking..."):
            response = call_groq(quick_prompt)
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            active_thread["messages"].append({"role": "assistant", "content": response, "timestamp": timestamp})

        st.session_state.welcome_action = None
        st.rerun()

else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-bubble user-bubble">
                    {msg['content']}
                    <div class="message-timestamp">{msg.get('timestamp', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-bubble assistant-bubble">
                    {msg['content']}
                    <div class="message-timestamp">{msg.get('timestamp', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# INPUT BAR
st.markdown("""
<div class="chat-input-container">
    <div class="chat-input-row">
""", unsafe_allow_html=True)

col_text, col_attach, col_mic = st.columns([7, 1, 1])

with col_text:
    current_input_id = f"user_input_{st.session_state.active_thread_id}"
    user_input = st.text_input(
        "",
        placeholder="Type message... ⏎ Enter to send",
        key=current_input_id,
        label_visibility="collapsed",
        help="Press Enter to send"
    )

with col_attach:
    attach_clicked = st.button("📎", key="attach_btn_unique", help="Attach file")

with col_mic:
    mic_clicked = st.button("🎤", key="mic_btn_unique", help="Voice input")

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# ENTER KEY HANDLER (code fixer wrapper)
current_input_id = f"user_input_{st.session_state.active_thread_id}"
if (
    current_input_id not in st.session_state.last_input_length or
    st.session_state.last_input_length.get(current_input_id, 0) != len(user_input) and
    user_input.strip()
):
    st.session_state.last_input_length[current_input_id] = len(user_input)

    if user_input.strip():
        base_prompt = user_input.strip()

        # Base wrapper: always treat as code fixing
        full_prompt = (
            "Act as a code fixer. Analyze and fix any code, configuration, or error messages in this input.\n\n"
            f"{base_prompt}"
        )
        user_content = base_prompt

        if st.session_state.get("ocr_text"):
            full_prompt = (
                "Act as a code fixer.\n"
                "Here is file content followed by my question.\n\n"
                f"File content:\n{st.session_state.ocr_text}\n\n"
                f"Question:\n{base_prompt}"
            )
            user_content = f"📎 File + {base_prompt}"
            st.session_state.ocr_text = None

        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "content": user_content, "timestamp": timestamp})
        active_thread["messages"].append({"role": "user", "content": user_content, "timestamp": timestamp})

        update_thread_title(st.session_state.active_thread_id, user_content)

        with st.spinner("🤖 Thinking..."):
            response = call_groq(full_prompt)
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            active_thread["messages"].append({"role": "assistant", "content": response, "timestamp": timestamp})

        st.rerun()

# FILE UPLOADER MODAL
if st.session_state.get('show_file_uploader', False):
    st.markdown("""
    <div class="file-uploader-container">
    """, unsafe_allow_html=True)

    st.markdown("### 📎 Upload File")
    uploaded_file = st.file_uploader(
        "",
        type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'py'],
        key=f"uploader_{st.session_state.active_thread_id}"
    )

    col_cancel, col_process = st.columns([1, 1])
    with col_cancel:
        if st.button("❌ Cancel", key="cancel_upload"):
            st.session_state.show_file_uploader = False
            st.rerun()

    with col_process:
        if st.button("✅ Process", key="process_upload") and uploaded_file:
            with st.spinner("Processing file and sending to model..."):
                text = process_ocr(uploaded_file)
                if text:
                    st.session_state.ocr_text = text

                    full_prompt = (
                        "You are a code fixer.\n"
                        "Below is text extracted from an uploaded file. It may contain code, error logs, or configuration.\n\n"
                        f"{text}\n\n"
                        "Tasks:\n"
                        "1) Detect any bugs or errors.\n"
                        "2) Explain the problem.\n"
                        "3) Provide corrected code or configuration.\n"
                        "4) If no obvious bug, suggest improvements and best practices."
                    )

                    timestamp = datetime.now().strftime("%H:%M")
                    user_content = "📎 Image/file uploaded (OCR text sent to model)"
                    st.session_state.messages.append(
                        {"role": "user", "content": user_content, "timestamp": timestamp}
                    )
                    active_thread["messages"].append(
                        {"role": "user", "content": user_content, "timestamp": timestamp}
                    )
                    update_thread_title(st.session_state.active_thread_id, user_content)

                    response = call_groq(full_prompt)
                    timestamp = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response, "timestamp": timestamp}
                    )
                    active_thread["messages"].append(
                        {"role": "assistant", "content": response, "timestamp": timestamp}
                    )

                    st.session_state.show_file_uploader = False
                    st.success(f"✅ OCR complete & sent to model ({len(text)} chars)", icon="🔍")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ATTACH BUTTON HANDLER
if attach_clicked:
    st.session_state.show_file_uploader = True
    st.rerun()

# MIC HANDLER (also as code fixer)
if mic_clicked:
    st.info("🎤 Listening...")
    text = speech_to_text()
    if text:
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "content": f"🎤 {text}", "timestamp": timestamp})
        active_thread["messages"].append({"role": "user", "content": f"🎤 {text}", "timestamp": timestamp})

        full_prompt = (
            "Act as a code fixer. Analyze and fix any code or errors mentioned in this spoken input.\n\n"
            f"{text}"
        )

        with st.spinner("🤖 Processing speech..."):
            response = call_groq(full_prompt)
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
            active_thread["messages"].append({"role": "assistant", "content": response, "timestamp": timestamp})

        update_thread_title(st.session_state.active_thread_id, text)
        st.rerun()
    else:
        st.warning("❌ No speech detected")
        st.rerun()
