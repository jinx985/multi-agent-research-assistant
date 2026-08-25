# app/tools/search.py
"""搜索工具封装：多引擎 + 自动降级

搜索策略（按优先级）：
1. Tavily（AI 专用搜索，推荐！免费注册 https://tavily.com，每月 1000 次）
2. Bing（国内可用，无需 Key，直接抓取网页结果）
3. DuckDuckGo（免费，但国内网络不稳定）

任一引擎失败自动降级到下一个，保证搜索不中断。
"""

import os
import re
from urllib.parse import quote_plus

from langchain_core.tools import tool


def _search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Tavily 搜索（需要 TAVILY_API_KEY）"""
    import requests

    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY 未配置")

    resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": api_key, "query": query, "max_results": max_results},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    return [
        {
            "title": r.get("title", ""),
            "href": r.get("url", ""),
            "body": r.get("content", ""),
        }
        for r in data.get("results", [])
    ]


def _search_bing(query: str, max_results: int = 5) -> list[dict]:
    """Bing 搜索（国内可用，零配置，直接解析网页）"""
    import requests
    from bs4 import BeautifulSoup

    url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
    resp = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        },
        timeout=15,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for li in soup.select("li.b_algo")[:max_results]:
        a = li.select_one("h2 a")
        if not a:
            continue
        snippet = li.select_one(".b_caption p") or li.select_one("p")
        results.append(
            {
                "title": a.get_text(strip=True),
                "href": a.get("href", ""),
                "body": snippet.get_text(strip=True) if snippet else "",
            }
        )
    return results


def _search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo 搜索（免费，但国内网络不稳定）"""
    from duckduckgo_search import DDGS

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", ""),
                }
            )
    return results


# 引擎列表（按优先级排列，自动降级）
_ENGINES = [
    ("Tavily", _search_tavily),
    ("Bing", _search_bing),
    ("DuckDuckGo", _search_duckduckgo),
]


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    搜索互联网获取最新信息（自动选择可用引擎）

    Args:
        query: 搜索关键词
        max_results: 最大结果数（默认5条）

    Returns:
        格式化的搜索结果，包含标题、链接和摘要
    """
    last_error = None

    for engine_name, engine_fn in _ENGINES:
        try:
            results = engine_fn(query, max_results)
            if results:
                formatted = "\n\n".join(
                    f"- [{r['title']}]({r['href']})\n  {r['body'][:200]}..."
                    for r in results
                )
                return f"（来源：{engine_name}）\n\n{formatted}"
        except Exception as e:
            last_error = f"{engine_name}: {e}"
            continue

    # 全部引擎失败：返回友好提示（不抛异常，让流程继续）
    return (
        f"搜索「{query}」暂不可用（{last_error}）。"
        "请基于已有知识进行回答，并注明信息来源可能存在局限。"
    )


# 给 LLM 的工具描述里包含提示（便于 Agent 理解）
web_search.description = (
    "搜索互联网获取最新信息。自动选择可用搜索引擎（Tavily/Bing/DuckDuckGo）。"
    "返回结果为格式化文本，包含标题、链接和摘要。"
)
