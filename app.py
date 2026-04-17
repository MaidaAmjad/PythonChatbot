import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import urllib.parse
import requests
from datetime import datetime

# Load .env file 
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-flash-latest")
HISTORY_FILE = "chat_history.json"

# --- Helper Functions ---

def load_all_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {"Default Chat": data}
                return data
        except Exception:
            return {"New Chat": []}
    return {"New Chat": []}

def save_all_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.chat_sessions, f, indent=2)

# --- Session State Initialization ---

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_all_history()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]

if "chat_objects" not in st.session_state:
    st.session_state.chat_objects = {}

# Ensure current session has a Gemini chat object
if st.session_state.current_chat_id not in st.session_state.chat_objects:
    messages = st.session_state.chat_sessions[st.session_state.current_chat_id]
    history_data = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        history_data.append({"role": role, "parts": [msg["content"]]})
    
    sys_prompt = "You are Nocturnal Intelligence, a premium AI assistant. You can describe images, but you CANNOT generate them yourself. However, if a user asks you to 'draw' or 'generate an image', I (the system) will handle the generation. Just provide an encouraging text response. DO NOT output JSON tool calls."
    st.session_state.chat_objects[st.session_state.current_chat_id] = model.start_chat(history=history_data)

# --- UI Setup ---
st.set_page_config(page_title="Nocturnal Intelligence", page_icon="✨", layout="wide")

@st.cache_data(show_spinner=False)
def fetch_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.error(f"Image fetch error: {e}")
    return None

# Native CSS Injection (No Tailwind Dependency)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

<style>
    /* Reset and Global */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #060e20 !important;
        color: #dee5ff !important;
        font-family: 'Inter', sans-serif;
    }
    
    header, footer, .stDeployButton {display: none !important;}
    
    [data-testid="stSidebar"] {
        background-color: #091328 !important;
        width: 300px !important;
        border: none !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #192540; border-radius: 10px; }

    /* Custom Navigation Buttons */
    .nav-button {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 12px;
        color: #a3aac4;
        font-family: 'Manrope', sans-serif;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: 0.3s;
        border: none;
        background: transparent;
        width: 100%;
        text-align: left;
    }
    .nav-button:hover {
        background: #0f1930;
        color: #dee5ff;
    }
    .nav-button.active {
        background: #192540;
        color: #ba9eff;
    }
    
    /* Session Buttons in Sidebar */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #a3aac4 !important;
        text-align: left !important;
        padding: 10px 16px !important;
        width: 100% !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    .stButton > button:hover {
        background: #0f1930 !important;
        color: #dee5ff !important;
    }
    .active-chat > div > button {
        background: #192540 !important;
        color: #ba9eff !important;
    }

    /* Delete Button Styling - Force Red and Transparent */
    [data-testid="stSidebar"] button:has(span[aria-label="delete icon"]) {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: unset !important;
        width: 32px !important;
        height: 32px !important;
    }
    
    [data-testid="stSidebar"] span[aria-label="delete icon"] {
        color: #ff0000 !important;
        font-size: 20px !important;
    }

    [data-testid="stSidebar"] button:has(span[aria-label="delete icon"]):hover {
        background-color: rgba(255, 0, 0, 0.1) !important;
    }
    
    [data-testid="column"] {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        flex-direction: row !important;
        align-items: center !important;
    }

    /* Main Branding Logo */
    .brand-logo {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #ba9eff, #8455ef);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* New Chat Button */
    .new-chat-btn {
        background: linear-gradient(90deg, #ba9eff, #8455ef) !important;
        color: #39008c !important;
        font-weight: 800 !important;
        border-radius: 50px !important;
        padding: 16px !important;
        justify-content: center !important;
        box-shadow: 0 4px 15px rgba(186, 158, 255, 0.2);
    }
    
    /* Welcome Screen Styling */
    .welcome-title {
        font-family: 'Manrope', sans-serif;
        font-size: 48px;
        font-weight: 900;
        letter-spacing: -2px;
        line-height: 1;
        margin-bottom: 16px;
    }
    .welcome-subtitle {
        color: #a3aac4;
        font-size: 16px;
        max-width: 500px;
        line-height: 1.6;
    }
    
    /* Recommendation Cards */
    .suggestion-card {
        background: #091328;
        border: 1px solid rgba(109, 117, 140, 0.1);
        padding: 24px;
        border-radius: 20px;
        transition: 0.3s;
        cursor: pointer;
    }
    .suggestion-card:hover {
        background: #0f1930;
        border-color: #ba9eff;
    }

    /* Sidebar Spacing Fix */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0px !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }

    /* Fixed Input Area and White Box Fix */
    [data-testid="stBottomBlockContainer"] {
        background-color: #060e20 !important;
        padding-bottom: 2rem !important;
    }
    
    [data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border: 1px solid rgba(109, 117, 140, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Chat Bubbles */
    .msg-user {
        background-color: #ae8dff;
        color: #2b006e;
        padding: 16px 20px;
        border-radius: 18px 18px 2px 18px;
        font-size: 14px;
        font-weight: 500;
        max-width: 85%;
        align-self: flex-end;
    }
    .msg-bot {
        background-color: #192540;
        color: #dee5ff;
        padding: 16px 20px;
        border-radius: 18px 18px 18px 2px;
        font-size: 14px;
        max-width: 85%;
        border: 1px solid rgba(186, 158, 255, 0.1);
    }
    
    /* Profile Image Fix */
    .avatar-img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
    }
    .sidebar-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        object-fit: cover;
    }

    /* Image Message Styling */
    .img-msg-container {
        margin-top: 12px;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(186, 158, 255, 0.2);
    }
    .img-msg-container img {
        width: 100%;
        height: auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---

with st.sidebar:
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 32px; padding: 10px;">
        <div class="brand-logo">
            <span class="material-symbols-outlined" style="color: #39008c; font-variation-settings: 'FILL' 1;">auto_awesome</span>
        </div>
        <div>
            <h1 style="margin:0; font-family:'Manrope'; font-size: 20px; font-weight:800; color:#dee5ff;">Nocturnal Intelligence</h1>
            <p style="margin:0; font-size: 10px; font-weight:700; color:#8455ef; text-transform:uppercase; tracking-widest: 1px;">Premium Tier</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat
    if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
        new_id = f"Chat {datetime.now().strftime('%H:%M:%S')}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_chat_id = new_id
        st.session_state.chat_objects[new_id] = model.start_chat(history=[])
        st.rerun()
    
    st.markdown("<p style='font-size: 10px; font-weight:800; color:#6d758c; text-transform:uppercase; margin: 24px 0 8px 16px;'>Main</p>", unsafe_allow_html=True)
    
    # Static Nav
    st.markdown("""
    <div class="nav-button active"><span class="material-symbols-outlined">history</span> Recent Chats</div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 10px; font-weight:800; color:#6d758c; text-transform:uppercase; margin: 24px 0 8px 16px;'>History</p>", unsafe_allow_html=True)

    # Chat History List
    for chat_id in reversed(list(st.session_state.chat_sessions.keys())):
        history = st.session_state.chat_sessions[chat_id]
        if history:
            first = history[0]["content"]
            label = (first[:25] + "...") if len(first) > 25 else first
        else:
            label = chat_id
            
        active_class = "active-chat" if chat_id == st.session_state.current_chat_id else ""
        
        # UI Columns for Chat Selection and Deletion
        col_chat, col_del = st.columns([0.88, 0.12])
        
        with col_chat:
            st.markdown(f'<div class="{active_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"chat_item_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_del:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button(":material/delete:", key=f"del_{chat_id}", help="Delete Chat"):
                # Delete logic
                del st.session_state.chat_sessions[chat_id]
                if chat_id in st.session_state.chat_objects:
                    del st.session_state.chat_objects[chat_id]
                
                # Update current chat if needed
                if st.session_state.current_chat_id == chat_id:
                    remaining_chats = list(st.session_state.chat_sessions.keys())
                    if remaining_chats:
                        st.session_state.current_chat_id = remaining_chats[0]
                    else:
                        # If no chats left, create a new one
                        new_id = f"Chat {datetime.now().strftime('%H:%M:%S')}"
                        st.session_state.chat_sessions[new_id] = []
                        st.session_state.current_chat_id = new_id
                
                save_all_history()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.html("""
    <div style="margin-top: auto; padding-top: 24px; border-top: 1px solid rgba(109, 117, 140, 0.1);">
        <div style="display: flex; align-items: center; gap: 12px; padding: 8px;">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Maida" style="width: 40px; height: 40px; border-radius: 12px; object-fit: cover;">
            <div style="overflow: hidden;">
                <p style="margin:0; font-family:'Inter'; font-size: 14px; font-weight:700; color:#dee5ff;">Maida Amjad</p>
                <p style="margin:0; font-family:'Inter'; font-size: 12px; color:#6d758c; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">maidaamjad32@gmail.com</p>
            </div>
        </div>
    </div>
    """)

# --- Main Canvas ---

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]

# Top Bar
st.html("""
<div style="position: sticky; top: 0; min-height: 64px; background: rgba(6, 14, 32, 0.6); backdrop-filter: blur(20px); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; z-index: 100; border-bottom: 1px solid rgba(186, 158, 255, 0.1);">
    <h2 style="margin:0; font-family:'Manrope'; font-size: 18px; font-weight:900; color:#dee5ff;">Recent Chats</h2>
    <div style="display: flex; align-items: center; gap: 24px; color: #ba9eff;">
        <span class="material-symbols-outlined">help_outline</span>
        <span class="material-symbols-outlined">account_circle</span>
    </div>
</div>
""")

if not current_chat:
    # Welcome
    st.html("""
<div style="max-width: 800px; margin: 48px auto; padding: 0 24px; font-family: 'Inter', sans-serif;">
    <h3 style="font-family:'Manrope'; font-size: 48px; font-weight:900; letter-spacing:-2px; line-height:1; margin-bottom:16px; color:#dee5ff;">Good evening,<br><span style="color:#ba9eff;">how can I assist?</span></h3>
    <p style="color:#a3aac4; font-size:16px; max-width:500px; line-height:1.6; margin-bottom:48px;">I am your high-performance neural concierge. From complex data analysis to creative syntheses, I operate at the edge of the void.</p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
        <div style="background:#091328; border:1px solid rgba(109,117,140,0.1); padding:24px; border-radius:20px; transition:0.3s;">
            <div style="width:40px; height:40px; background:#192540; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#ba9eff; margin-bottom:16px;">
                <span class="material-symbols-outlined">code</span>
            </div>
            <h4 style="margin:0; font-family:'Manrope'; font-weight:700; font-size:16px; color:#dee5ff;">Analyze Python Script</h4>
            <p style="margin:8px 0 0 0; font-size:12px; color:#a3aac4;">Review legacy code for optimization and vulnerability patches.</p>
        </div>
        <div style="background:#091328; border:1px solid rgba(109,117,140,0.1); padding:24px; border-radius:20px; transition:0.3s;">
            <div style="width:40px; height:40px; background:#192540; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#ffa5d9; margin-bottom:16px;">
                <span class="material-symbols-outlined">edit_note</span>
            </div>
            <h4 style="margin:0; font-family:'Manrope'; font-weight:700; font-size:16px; color:#dee5ff;">Draft Executive Summary</h4>
            <p style="margin:8px 0 0 0; font-size:12px; color:#a3aac4;">Synthesize the Q3 market trends into a concise board-ready brief.</p>
        </div>
    </div>
</div>
""")
else:
    # Messages
    st.markdown('<div style="max-width: 800px; margin: 48px auto; display: flex; flex-direction: column; gap: 40px; padding: 0 24px;">', unsafe_allow_html=True)
    for msg in current_chat:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; gap: 16px; align-self: flex-end; flex-direction: row-reverse; max-width: 85%;">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" class="avatar-img">
                <div class="msg-user">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bot Message Container
            with st.container():
                st.markdown(f"""
                <div style="display: flex; gap: 16px; max-width: 85%; margin-bottom: 24px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #192540; display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: relative;">
                        <div style="position: absolute; inset: 0; border-radius: 50%; background: rgba(132, 85, 239, 0.2); filter: blur(8px); transform: scale(1.5);"></div>
                        <span class="material-symbols-outlined" style="color: #ba9eff; font-size: 16px; font-variation-settings: 'FILL' 1;">auto_awesome</span>
                    </div>
                    <div class="msg-bot">
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if "image_url" in msg:
                    # Render the image inside the same logical block but using Streamlit native command
                    cols = st.columns([0.1, 0.8, 0.1])
                    with cols[1]:
                        img_bytes = fetch_image(msg["image_url"])
                        if img_bytes:
                            st.image(img_bytes, use_container_width=True)
                        else:
                            st.warning("Failed to render image.")

# Chat Input
if prompt := st.chat_input("Type your message..."):
    # Session Renaming Logic
    is_new = st.session_state.current_chat_id.startswith("Chat ") and not current_chat
    
    # Intent Detection for Image Generation
    draw_keywords = ["draw", "generate image", "create image", "generate a picture", "make a picture", "show me a picture"]
    is_draw = any(kw in prompt.lower() for kw in draw_keywords)
    
    # Store user message
    st.session_state.chat_sessions[st.session_state.current_chat_id].append({"role": "user", "content": prompt})
    
    image_url = None
    if is_draw:
        # Extract prompt for image generation
        img_prompt = prompt
        for kw in draw_keywords:
            img_prompt = img_prompt.lower().replace(kw, "").strip()
        
        if not img_prompt:
            img_prompt = prompt
        
        # Construct Pollinations URL with proper encoding and the direct image endpoint
        encoded_prompt = urllib.parse.quote(img_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={datetime.now().microsecond}&nologo=true"

    if is_new:
        base = prompt[:20].strip() or "New Chat"
        new_id = base
        count = 1
        while new_id in st.session_state.chat_sessions:
            new_id = f"{base} ({count})"
            count += 1
        st.session_state.chat_sessions[new_id] = st.session_state.chat_sessions.pop(st.session_state.current_chat_id)
        st.session_state.chat_objects[new_id] = st.session_state.chat_objects.pop(st.session_state.current_chat_id)
        st.session_state.current_chat_id = new_id

    # Get Bot reply
    try:
        chat_obj = st.session_state.chat_objects[st.session_state.current_chat_id]
        if is_draw:
            reply = f"I've visualized that for you: '{img_prompt}'. Bringing it to life now..."
        else:
            response = chat_obj.send_message(prompt)
            reply = response.text
    except Exception as e:
        reply = f"System Error: {e}"

    # Store bot message
    bot_msg = {"role": "assistant", "content": reply}
    if image_url:
        bot_msg["image_url"] = image_url
    
    st.session_state.chat_sessions[st.session_state.current_chat_id].append(bot_msg)
    
    save_all_history()
    st.rerun()

# Bottom Badge
st.markdown("""
<div style="text-align: center; padding: 24px 0; opacity: 0.5;">
    <p style="font-size: 10px; font-weight: 700; color: #6d758c; text-transform: uppercase; letter-spacing: 2px;">Encrypted Session • Enterprise Grade Security</p>
</div>
""", unsafe_allow_html=True)
