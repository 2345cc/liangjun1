"""辅助函数模块"""

import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime


def setup_page(title="🤖 AI Chatbot", layout="wide"):
    st.set_page_config(page_title=title, page_icon="🤖", layout=layout)
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def init_session_state():
    """初始化所有会话状态"""
    defaults = {
        "messages_display": [],
        "backend": "ollama",
        "current_response": "",
        "model_config": {
            "base_url": "http://localhost:11434",
            "model": "deepseek-r1:7b"
        }
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def markdown_to_html(text):
    """将文本转为安全HTML（保留基本格式）"""
    import html
    return html.escape(text).replace("\n", "<br>")