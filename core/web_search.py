"""联网搜索模块 - 支持多引擎搜索"""

import requests
from bs4 import BeautifulSoup


def search_web(query, num_results=5):
    """联网搜索，自动选择可用引擎，返回 (success, results_str)"""
    results = None

    try:
        results = _search_duckduckgo(query, num_results)
    except Exception:
        pass

    if not results:
        try:
            results = _search_bing(query, num_results)
        except Exception:
            pass

    if not results:
        return False, "所有搜索引擎均不可用，请稍后再试"

    formatted = _format_results(query, results)
    return True, formatted


def _search_duckduckgo(query, num_results=5):
    """DuckDuckGo 搜索（免费，无需API Key）"""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    data = {"q": query}

    resp = requests.post(url, data=data, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for item in soup.select(".result")[:num_results]:
        title_el = item.select_one(".result__title a")
        snippet_el = item.select_one(".result__snippet")

        if title_el:
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if link.startswith("//"):
                link = "https:" + link
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            results.append({"title": title, "url": link, "snippet": snippet})

    return results


def _search_bing(query, num_results=5):
    """Bing 中文搜索（国内可用）"""
    url = "https://cn.bing.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"q": query, "cc": "cn", "mkt": "zh-CN"}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for item in soup.select(".b_algo")[:num_results]:
        title_el = item.select_one("h2 a")
        snippet_el = item.select_one(".b_caption p")

        if title_el:
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            results.append({"title": title, "url": link, "snippet": snippet})

    return results


def _format_results(query, results):
    """将搜索结果格式化为上下文文本"""
    if not results:
        return f"关于「{query}」没有找到相关结果。"

    lines = [
        f"## 联网搜索结果: {query}",
        "",
        f"为用户搜索到以下 {len(results)} 条相关信息，请基于这些信息回答用户的问题：",
        ""
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r['title']}")
        lines.append(f"   来源: {r['url']}")
        if r['snippet']:
            lines.append(f"   摘要: {r['snippet']}")
        lines.append("")

    lines.append("请基于以上搜索结果回答用户的问题，如果搜索结果不足以回答，请如实告知。")
    lines.append("在回答中适当引用信息来源（标注序号）。")

    return "\n".join(lines)


def check_search_available():
    """检查搜索引擎是否可用"""
    try:
        ok, _ = search_web("test", 1)
        return ok
    except Exception:
        return False