"""侧边栏配置组件 - 模型选择、参数调节、历史管理"""

import streamlit as st
from core.prompt_templates import get_template_names, get_prompt, get_description
from data.history_store import list_conversations, load_conversation, delete_conversation, save_conversation
from core.llm_client import LLMClient
from core.web_search import check_search_available


def render_sidebar():
    """渲染侧边栏配置"""
    with st.sidebar:
        st.markdown("## ⚙️ 配置")

        with st.expander("🤖 模型选择", expanded=True):
            backend = st.radio(
                "选择后端",
                options=["mock", "ollama", "deepseek"],
                format_func=lambda x: {
                    "mock": "🔄 模拟模式 (离线)",
                    "ollama": "🦙 Ollama (本地)",
                    "deepseek": "🌐 DeepSeek API"
                }.get(x, x),
                key="backend"
            )

            model_config = {}
            if backend == "mock":
                st.success("✅ 模拟模式 - 无需任何配置，离线可用")
                model_config = {"mode": "mock"}

            elif backend == "ollama":
                ollama_ok, detail = LLMClient.check_backend("ollama", {"base_url": "http://localhost:11434"})
                if ollama_ok:
                    _, models = LLMClient.check_ollama_status()
                    st.success(f"✅ Ollama 已连接 ({len(models)} 个模型)")
                    model = st.selectbox(
                        "选择模型",
                        options=models if models else ["deepseek-r1:7b"],
                        key="ollama_model"
                    )
                else:
                    st.error(f"❌ Ollama {detail}")
                    st.caption("启动方式: 终端运行 `ollama serve`")
                    model = st.text_input("模型名称", value="deepseek-r1:7b",
                                          key="ollama_model")
                model_config = {
                    "base_url": "http://localhost:11434",
                    "model": st.session_state.get("ollama_model", "deepseek-r1:7b")
                }

            else:
                api_key = st.text_input(
                    "DeepSeek API Key",
                    type="password",
                    value=st.session_state.get("deepseek_api_key", ""),
                    key="deepseek_api_key_input",
                    help="在 https://platform.deepseek.com 获取"
                )
                if api_key:
                    st.session_state["deepseek_api_key"] = api_key
                    st.success("✅ API Key 已配置")
                else:
                    st.warning("⚠️ 请输入 API Key")

                model = st.selectbox(
                    "选择模型",
                    options=["deepseek-chat", "deepseek-reasoner"],
                    key="deepseek_model"
                )
                model_config = {
                    "api_key": api_key,
                    "base_url": "https://api.deepseek.com",
                    "model": model
                }

            st.session_state["model_config"] = model_config

        with st.expander("🎯 参数调节", expanded=False):
            temperature = st.slider("温度 (Temperature)", 0.0, 2.0, 0.7, 0.1,
                                    help="越高越有创造性，越低越确定性")
            max_tokens = st.slider("最大Token数", 256, 8192, 2048, 256)
            top_p = st.slider("Top-P", 0.0, 1.0, 0.9, 0.05)

        with st.expander("🌐 联网搜索", expanded=True):
            search_ok = check_search_available()
            if search_ok:
                st.success("✅ 搜索引擎可用 · 每次对话自动联网")
                st.caption("自动搜索你的问题，将结果提供给AI参考")
            else:
                st.warning("⚠️ 搜索引擎暂时不可用")
                st.caption("对话仍可正常进行，AI将基于自身知识回答")
                if st.button("🔄 重试检测", use_container_width=True):
                    st.rerun()

        with st.expander("📝 系统提示词", expanded=True):
            template_names = get_template_names()
            selected_template = st.selectbox(
                "选择提示词模板",
                template_names,
                key="prompt_template"
            )
            desc = get_description(selected_template)
            if desc:
                st.caption(desc)

            prompt_content = get_prompt(selected_template)
            custom_prompt = st.text_area(
                "自定义提示词（可编辑）",
                value=prompt_content,
                height=120,
                key="system_prompt"
            )

        with st.expander("💬 对话管理", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ 清空对话", use_container_width=True):
                    st.session_state.messages_display = []
                    cm = st.session_state.get("chat_manager")
                    if cm:
                        cm.clear()
                    st.rerun()
            with col2:
                if st.button("💾 保存对话", use_container_width=True):
                    cm = st.session_state.get("chat_manager")
                    if cm and len(cm.messages) > 1:
                        convo_id = save_conversation(
                            cm.to_dict(),
                            title=f"对话_{len(cm.messages)}条"
                        )
                        st.success(f"已保存 (ID: {convo_id[:8]}...)")
                    else:
                        st.warning("暂无消息可保存")

            st.markdown("**📂 历史记录**")
            conversations = list_conversations()
            if conversations:
                for conv in conversations[:10]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        label = f"{conv['title'][:20]} ({conv['message_count']}条)"
                        if st.button(label, key=f"load_{conv['id']}",
                                     use_container_width=True):
                            data = load_conversation(conv["id"])
                            if data:
                                from core.chat_manager import ChatManager
                                cm = ChatManager.from_dict(data["data"])
                                st.session_state.chat_manager = cm
                                display = [m for m in cm.messages
                                           if m["role"] != "system"]
                                st.session_state.messages_display = display
                                st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_{conv['id']}"):
                            delete_conversation(conv["id"])
                            st.rerun()
            else:
                st.caption("暂无历史记录")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.8rem;">
            🤖 Streamlit Chatbot<br>
            模拟模式 / Ollama / DeepSeek
        </div>
        """, unsafe_allow_html=True)

    return backend, temperature, max_tokens, top_p