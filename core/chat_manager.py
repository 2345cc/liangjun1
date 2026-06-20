"""对话管理模块 - 管理消息历史、上下文窗口"""

import streamlit as st


class ChatManager:
    """管理单轮对话的消息列表和上下文窗口"""

    def __init__(self, system_prompt=None, max_turns=20):
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def set_system_prompt(self, prompt):
        """设置或更新系统提示词"""
        self.system_prompt = prompt
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})

    def trim_context(self):
        """裁剪上下文到最大轮次（保留system prompt）"""
        non_system = [m for m in self.messages if m["role"] != "system"]
        system = [m for m in self.messages if m["role"] == "system"]

        if len(non_system) > self.max_turns * 2:
            excess = len(non_system) - self.max_turns * 2
            non_system = non_system[excess:]

        self.messages = system + non_system

    def get_context_messages(self):
        """获取当前上下文消息（用于API调用）"""
        return self.messages

    def clear(self):
        """清空对话（保留system prompt）"""
        self.messages = []
        if self.system_prompt:
            self.messages.append({"role": "system", "content": self.system_prompt})

    def to_dict(self):
        return {
            "system_prompt": self.system_prompt,
            "max_turns": self.max_turns,
            "messages": self.messages
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            system_prompt=data.get("system_prompt"),
            max_turns=data.get("max_turns", 20)
        )
        instance.messages = data.get("messages", [])
        return instance


def init_chat_session():
    """初始化会话状态"""
    if "chat_manager" not in st.session_state:
        st.session_state.chat_manager = ChatManager(max_turns=20)
    if "messages_display" not in st.session_state:
        st.session_state.messages_display = []
    if "current_response" not in st.session_state:
        st.session_state.current_response = ""


def get_chat_manager():
    return st.session_state.chat_manager