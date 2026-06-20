"""CSS样式模块"""

import streamlit as st


def apply_chat_style():
    st.markdown("""
    <style>
        .stApp {
            background: #ffffff;
        }
        .main-header {
            text-align: center;
            padding: 0.8rem 0 0 0;
        }
        .main-header h1 {
            font-size: 1.8rem;
            color: #1a1a2e;
            margin-bottom: 0.2rem;
        }
        .main-header .subtitle {
            font-size: 0.85rem;
            color: #888;
        }
        .stChatMessage {
            padding: 8px 0;
        }
        .stChatMessage [data-testid="chatMessageContent"] {
            border-radius: 16px;
            padding: 10px 16px;
            line-height: 1.6;
        }
        .stChatInput {
            border-top: 1px solid #eee;
            padding-top: 12px;
        }
        .stChatInput textarea {
            border-radius: 20px !important;
            border: 1px solid #ddd !important;
            padding: 10px 16px !important;
        }
        .stChatInput button {
            border-radius: 20px !important;
            background: #4A90D9 !important;
            color: white !important;
        }
        .stButton button {
            border-radius: 8px;
            font-size: 0.85rem;
        }
        section[data-testid="stSidebar"] {
            background: #f8f9fa;
            border-right: 1px solid #eee;
        }
        section[data-testid="stSidebar"] .stExpander {
            background: white;
            border: 1px solid #eee;
            border-radius: 10px;
            margin-bottom: 8px;
        }
        section[data-testid="stSidebar"] .stExpander summary {
            font-weight: 500;
            padding: 8px 0;
        }
        .stRadio label {
            font-size: 0.9rem;
        }
        .stSelectbox label, .stSlider label {
            font-size: 0.85rem;
            color: #555;
        }
        .stAlert {
            font-size: 0.85rem;
        }
        hr {
            border-color: #eee !important;
        }
        div[data-testid="stChatMessageContent"] p {
            margin-bottom: 0;
        }
        div[data-testid="stChatMessageContent"] code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85rem;
        }
        div[data-testid="stChatMessageContent"] pre {
            background: #1e1e1e;
            border-radius: 10px;
            padding: 14px;
            overflow-x: auto;
        }
        div[data-testid="stChatMessageContent"] pre code {
            background: transparent;
            color: #d4d4d4;
            padding: 0;
        }
    </style>
    """, unsafe_allow_html=True)