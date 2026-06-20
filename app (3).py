"""🤖 AI Chatbot - 基于Streamlit的智能对话应用"""

import streamlit as st
from utils.helpers import setup_page, init_session_state
from ui.styles import apply_chat_style
from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_messages, render_empty_chat
from core.chat_manager import init_chat_session, get_chat_manager
from core.llm_client import LLMClient
from core.web_search import search_web

setup_page("🤖 AI Chatbot")
apply_chat_style()
init_session_state()
init_chat_session()

st.markdown("""
<div class="main-header">
    <h1>🤖 AI Chatbot</h1>
    <div class="subtitle">模拟模式 / Ollama 本地模型 / DeepSeek API · 支持联网搜索</div>
</div>
""", unsafe_allow_html=True)

backend, temperature, max_tokens, top_p = render_sidebar()

model_config = st.session_state.get("model_config", {})
ok, detail = LLMClient.check_backend(backend, model_config)
if ok:
    st.success(f"✅ **{backend.upper()}** · {detail}")
else:
    st.error(f"❌ **{backend.upper()}** · {detail}")

st.markdown("---")

system_prompt = st.session_state.get("system_prompt", "")
if system_prompt:
    get_chat_manager().set_system_prompt(system_prompt)

messages_display = st.session_state.messages_display

if messages_display:
    render_chat_messages(messages_display)
else:
    render_empty_chat()

prompt = st.chat_input("输入你的消息...")

if prompt:
    cm = get_chat_manager()
    cm.add_user_message(prompt)
    messages_display.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # --- 联网搜索阶段 ---
    web_context = None
    search_status = st.status("🌐 正在联网搜索...", expanded=False)
    try:
        search_ok, search_results = search_web(prompt)
        if search_ok:
            web_context = search_results
            search_status.update(
                label="✅ 联网搜索完成",
                state="complete",
                expanded=False
            )
        else:
            search_status.update(
                label="⚠️ 联网搜索不可用（不影响对话）",
                state="error",
                expanded=False
            )
    except Exception:
        search_status.update(
            label="⚠️ 联网搜索出错（不影响对话）",
            state="error",
            expanded=False
        )

    # --- AI 回复阶段 ---
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        if web_context:
            search_msg = {"role": "system", "content": web_context}
            context_messages = [search_msg] + cm.get_context_messages()
        else:
            context_messages = cm.get_context_messages()

        cm.trim_context()

        client = LLMClient(backend=backend, config=model_config)

        for chunk in client.stream_chat(
            messages=context_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        ):
            full_response += chunk
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    cm.add_assistant_message(full_response)
    messages_display.append({"role": "assistant", "content": full_response})
    st.session_state.messages_display = messages_display