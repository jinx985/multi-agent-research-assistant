# scripts/run_demo_real.py — 用真实模型跑一次完整研究流程
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import run_research

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI 对教育行业的影响"
    print(f"🚀 开始真实研究：{topic}")
    print("=" * 60)

    result = run_research(topic, stream=True)

    print("\n" + "=" * 60)
    print("📄 最终报告")
    print("=" * 60)
    print(result.get("report", "（无报告）"))

    print("\n" + "-" * 60)
    print(f"📊 执行统计:")
    print(f"  - 搜索摘要长度: {len(result.get('search_results', ''))} 字符")
    print(f"  - 分析内容长度: {len(result.get('analysis', ''))} 字符")
    print(f"  - 报告长度: {len(result.get('report', ''))} 字符")
    print(f"  - 错误记录: {result.get('errors', {}) or '无'}")
