# scripts/test_search.py — 测试多引擎搜索
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.search import web_search

if __name__ == "__main__":
    query = "2024 年诺贝尔奖 人工智能"
    print(f"🔍 搜索: {query}\n")
    result = web_search.invoke({"query": query, "max_results": 5})
    print(result[:1500])
