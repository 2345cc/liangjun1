"""聊天界面组件 - 消息气泡、输入区、流式响应显示"""

import streamlit as st


def render_chat_messages(messages):
    """渲染聊天消息列表"""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            continue

        is_user = role == "user"
        avatar = "🧑" if is_user else "🤖"
        align = "right" if is_user else "left"
        bg = "#d1e7ff" if is_user else "#f0f0f0"
        border_color = "#4A90D9" if is_user else "#666"

        with st.chat_message(role, avatar=avatar):
            st.markdown(content)


def render_streaming_response(placeholder, full_response):
    """渲染流式响应（逐步显示）"""
    placeholder.markdown(full_response + "▌")


def render_final_response(placeholder, full_response):
    """渲染完整响应"""
    placeholder.markdown(full_response)


def render_chat_input():
    """渲染聊天输入框"""
    prompt = st.chat_input("输入你的消息...")
    return prompt


def render_empty_chat():
    """空状态提示"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 64px; margin-bottom: 16px;">🤖</div>
            <h3 style="color: #333;">开始对话</h3>
            <p style="color: #888;">
                在下方输入消息开始与AI助手对话<br>
                左侧边栏可配置模型参数和系统提示词
            </p>
        </div>
        """, unsafe_allow_html=True)