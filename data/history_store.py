"""对话历史存储模块 - 持久化保存到JSON文件"""

import json
import os
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path(__file__).parent.parent / "history"


def ensure_history_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def save_conversation(conversation_data, title=None):
    """保存对话到JSON文件"""
    ensure_history_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if title:
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:30]
        filename = f"{timestamp}_{safe_title}.json"
    else:
        filename = f"{timestamp}.json"

    filepath = HISTORY_DIR / filename
    convo = {
        "id": filename.replace(".json", ""),
        "title": title or f"对话 {timestamp}",
        "created_at": timestamp,
        "updated_at": timestamp,
        "message_count": len(conversation_data.get("messages", [])),
        "data": conversation_data
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(convo, f, ensure_ascii=False, indent=2)
    return convo["id"]


def load_conversation(conversation_id):
    """加载指定对话"""
    filepath = HISTORY_DIR / f"{conversation_id}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def delete_conversation(conversation_id):
    """删除指定对话"""
    filepath = HISTORY_DIR / f"{conversation_id}.json"
    if filepath.exists():
        os.remove(filepath)
        return True
    return False


def list_conversations():
    """列出所有历史对话"""
    ensure_history_dir()
    conversations = []
    for f in sorted(HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                conversations.append({
                    "id": data.get("id", f.stem),
                    "title": data.get("title", f.stem),
                    "created_at": data.get("created_at", ""),
                    "message_count": data.get("message_count", 0)
                })
        except:
            continue
    return conversations


def update_conversation(conversation_id, conversation_data):
    """更新已存在的对话"""
    filepath = HISTORY_DIR / f"{conversation_id}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            convo = json.load(f)
        convo["updated_at"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        convo["data"] = conversation_data
        convo["message_count"] = len(conversation_data.get("messages", []))
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(convo, f, ensure_ascii=False, indent=2)
        return True
    return False