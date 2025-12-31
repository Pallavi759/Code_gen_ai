import streamlit as st
import pytesseract
import requests
from PIL import Image
from pdf2image import convert_from_bytes
import uuid
import re
import ast
import json

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
st.set_page_config(
    page_title="OCR + Local Code Fixer",
    page_icon="🛠️",
    layout="wide"
)
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chats[st.session_state.current_chat_id] = []
with st.sidebar:
    st.title("🛠️ Code Fixer")

    if st.button("➕ New Chat"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.chats[st.session_state.current_chat_id] = []

    st.divider()
    st.subheader("🕒 Chat History")

    for cid in st.session_state.chats:
        if st.button(f"Chat {cid[:6]}", key=cid):
            st.session_state.current_chat_id = cid

    st.divider()
    language = st.selectbox(
        "Programming Language",
        ["Python", "C", "C++", "Java", "JavaScript"]
    )

chat = st.session_state.chats[st.session_state.current_chat_id]
def clean_ocr(text):
    lines = text.splitlines()
    return "\n".join(
        l for l in lines
        if not re.search(r'Input In|Traceback|SyntaxError', l)
    )

def ocr_image(img):
    return clean_ocr(
        pytesseract.image_to_string(img, config="--oem 3 --psm 6")
    )

def ocr_pdf(pdf_bytes):
    pages = convert_from_bytes(pdf_bytes)
    text = ""
    for p in pages:
        text += pytesseract.image_to_string(p, config="--oem 3 --psm 6")
    return clean_ocr(text)
def detect_python_error(code):
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return str(e)
def fix_code_local(code, error, language):
    url = "http://localhost:11434/api/chat"

    MAX_CHARS = 800
    code = code[:MAX_CHARS]

    prompt = f"""
Fix this {language} code error:

Error:
{error}

Correct the code and return ONLY the fixed code.
"""

    payload = {
        "model": "qwen2.5:1.5b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line.decode())
                if "message" in data:
                    yield data["message"]["content"]
st.title("🧠 OCR + Local AI Code Fixer")

for msg in chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
uploaded_file = st.file_uploader(
    "📎 Upload code image or PDF",
    type=["png", "jpg", "jpeg", "pdf"]
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        code = ocr_pdf(uploaded_file.read())
    else:
        code = ocr_image(Image.open(uploaded_file))

    chat.append({
        "role": "user",
        "content": f"Uploaded code:\n```python\n{code}\n```"
    })

    with st.chat_message("user"):
        st.code(code, language="python")

    error = detect_python_error(code)

    if error is None:
        response = "✅ No syntax error detected."
        chat.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.success(response)
    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            fixed = ""

            for token in fix_code_local(code, error, language):
                fixed += token
                placeholder.markdown(f"```python\n{fixed}\n```")

        chat.append({"role": "assistant", "content": f"```python\n{fixed}\n```"})
user_prompt = st.chat_input("Paste code directly or upload another file...")

if user_prompt:
    chat.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    error = detect_python_error(user_prompt)

    if error is None:
        response = "✅ No syntax error detected."
        chat.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.success(response)
    else:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            fixed = ""

            for token in fix_code_local(user_prompt, error, language):
                fixed += token
                placeholder.markdown(f"```python\n{fixed}\n```")

        chat.append({"role": "assistant", "content": f"```python\n{fixed}\n```"})
