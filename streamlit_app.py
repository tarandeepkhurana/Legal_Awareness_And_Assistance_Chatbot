
import streamlit as st
import requests
import os 

# Backend URL
BACKEND_URL = "https://legal-awareness-and-assistance-chatbot-wllj.onrender.com"

# Page config
st.set_page_config(
    page_title="NyayaSahayak - Legal Aid Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Stylish single-line heading
st.markdown("""
<div style='text-align:center; line-height:1.2;'>
    <h1 style='color:#3B82F6; font-family:Arial, sans-serif; font-weight:bold; display:inline-block; font-size:2.8rem; margin:0;'>
        ⚖️ NyayaSahayak — Legal Aid Assistant
    </h1>
    <p style='color:#FFFFFF; font-size:1.3rem; margin-top:5px; font-weight:500; opacity:0.9;'>
        Get clear, bilingual legal guidance for women and children |
        महिलाओं और बच्चों के लिए स्पष्ट, द्विभाषी कानूनी मार्गदर्शन प्राप्त करें 
    </p>
</div>
""", unsafe_allow_html=True)

# Custom CSS for chat bubbles
st.markdown("""
    <style>
    /* Make assistant text more visible */
    .stChatMessage[data-testid="stChatMessage-assistant"] p {
        color: white !important;
        font-weight: 500;
    }

    /* Assistant message bubble background */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        border-radius: 15px;
        padding: 10px;
        color: white;
    }

    /* User message bubble */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, #1e90ff, #00bfff);
        border-radius: 15px;
        padding: 10px;
        color: white;
    }

    /* Make all chat text slightly bigger for readability */
    .stChatMessage p {
        font-size: 1rem;
        line-height: 1.4;
    }

    /* Optional: improve spacing between messages */
    .stChatMessage {
        margin-bottom: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Chat container
# Chat container for previous messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"<div>{msg['content']}</div>", unsafe_allow_html=True)

# User input
if user_input := st.chat_input("Type your question here..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_history.append({"role": "user", "text": user_input})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(f"<div>{user_input}</div>", unsafe_allow_html=True)

    # Create placeholder for assistant reply
    assistant_placeholder = st.empty()

    # Send to FastAPI backend
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "user_query": user_input,
                "conversation_history": st.session_state.conversation_history
            },
            timeout=60
        )
        response.raise_for_status()
        assistant_reply = response.json().get("assistant_reply", "Sorry, no response.")
    except Exception as e:
        assistant_reply = f"⚠️ Error: {str(e)}"

    # Append assistant reply to session state
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.session_state.conversation_history.append({"role": "assistant", "text": assistant_reply})

    # Display assistant reply in placeholder
    with assistant_placeholder.container():
        with st.chat_message("assistant"):
            st.markdown(f"<div style='font-size:16px'>{assistant_reply}</div>", unsafe_allow_html=True)


    

