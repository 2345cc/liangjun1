"""LLM客户端模块 - 支持Ollama本地模型、DeepSeek API和模拟模式"""

import json
import time
import random
import requests


class LLMClient:
    """统一的LLM客户端接口"""

    def __init__(self, backend="ollama", config=None):
        self.backend = backend
        self.config = config or {}

    def stream_chat(self, messages, temperature=0.7, max_tokens=2048, top_p=0.9):
        """流式对话生成"""
        if self.backend == "mock":
            return self._mock_stream(messages)
        elif self.backend == "ollama":
            return self._ollama_stream(messages, temperature, max_tokens)
        elif self.backend == "deepseek":
            return self._deepseek_stream(messages, temperature, max_tokens, top_p)
        else:
            yield "❌ 不支持的后端: " + self.backend

    def _mock_stream(self, messages):
        """模拟回复（离线可用，无需外部服务）"""
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        last_input = user_msgs[-1] if user_msgs else ""

        MOCK_RESPONSES = [
            "你好！我是AI智能体。请问有什么可以帮助你的？",
            "这个问题很有意思，让我来回答：根据已有的信息，我们可以从多个角度来分析。",
            "很高兴和你讨论这个话题！以下是我的理解：",
            "这是一个很好的问题。让我给你一个详细的解答。",
            "我明白了你的意思。从技术角度看，有几点值得注意：",
        ]

        base_reply = random.choice(MOCK_RESPONSES)
        for char in base_reply:
            yield char
            time.sleep(0.03)

        if last_input:
            reply_parts = [
                f"\n\n关于「{last_input[:20]}」这个话题，",
                "我们可以深入探讨其背后的原理和应用场景。",
                "如果你有更具体的问题，欢迎继续提问！"
            ]
            for part in reply_parts:
                for char in part:
                    yield char
                    time.sleep(0.02)

    def _ollama_stream(self, messages, temperature, max_tokens):
        """Ollama API 流式调用"""
        base_url = self.config.get("base_url", "http://localhost:11434")
        model = self.config.get("model", "deepseek-r1:7b")
        url = f"{base_url}/api/chat"

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        if "message" in chunk and "content" in chunk["message"]:
                            delta = chunk["message"]["content"]
                            yield delta
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.ConnectionError:
            yield self._error_msg(f"无法连接到 Ollama ({base_url})\n\n请确保已经运行: `ollama serve`")
        except requests.exceptions.Timeout:
            yield self._error_msg("Ollama 请求超时，模型可能正在加载，请稍后再试")
        except Exception as e:
            yield self._error_msg(f"Ollama 请求出错: {str(e)}")

    def _deepseek_stream(self, messages, temperature, max_tokens, top_p):
        """DeepSeek API 流式调用"""
        api_key = self.config.get("api_key", "")
        base_url = self.config.get("base_url", "https://api.deepseek.com")
        model = self.config.get("model", "deepseek-chat")

        if not api_key:
            yield self._error_msg("请先在左侧边栏配置 DeepSeek API Key")
            return

        url = f"{base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }

        try:
            response = requests.post(url, json=payload, headers=headers,
                                     stream=True, timeout=60)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.ConnectionError:
            yield self._error_msg(f"无法连接到 DeepSeek API ({base_url})")
        except requests.exceptions.Timeout:
            yield self._error_msg("DeepSeek API 请求超时，请检查网络连接")
        except Exception as e:
            yield self._error_msg(f"DeepSeek 请求出错: {str(e)}")

    def _error_msg(self, text):
        return f"""⚠️ **回复失败**

{text}

---

💡 **建议：**
- 切换到 **🔄 模拟模式**（侧边栏 → 模型选择 → 模拟模式）体验离线对话
- 或检查后端服务状态后重试"""

    @staticmethod
    def check_backend(backend, config=None):
        """检查指定后端是否可用，返回 (可用, 详情)"""
        config = config or {}
        if backend == "mock":
            return True, "离线可用"
        elif backend == "ollama":
            base_url = config.get("base_url", "http://localhost:11434")
            try:
                resp = requests.get(f"{base_url}/api/tags", timeout=3)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    return True, f"已连接 ({len(models)} 个模型)"
                return False, "Ollama 服务异常"
            except:
                return False, "Ollama 未运行"
        elif backend == "deepseek":
            api_key = config.get("api_key", "")
            if api_key:
                return True, "API Key 已配置"
            return False, "未配置 API Key"
        return False, "不支持的后端"