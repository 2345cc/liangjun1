"""配置管理模块"""

import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 默认配置
DEFAULT_CONFIG = {
    "backend": "ollama",  # ollama / deepseek
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "deepseek-r1:7b",
        "available_models": ["deepseek-r1:7b", "deepseek-r1:14b", "deepseek-r1:32b",
                             "qwen2.5:7b", "qwen2.5:14b", "llama3:8b", "mistral:7b"]
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "available_models": ["deepseek-chat", "deepseek-reasoner"]
    },
    "chat": {
        "max_history_turns": 20,
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
    }
}


def get_config_path():
    """获取配置文件路径"""
    return ROOT_DIR / "config" / "config.json"


def load_config():
    """加载配置文件，不存在则使用默认配置"""
    import json
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(user_config)
            return merged
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置文件"""
    import json
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)