# scripts/test_llm.py — 快速测试模型连通性
import os
import sys
from pathlib import Path

# 把项目根目录加入模块搜索路径（方便从 scripts/ 目录运行）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from app.llm import create_chat_model

model = os.getenv("MODEL_NAME", "qwen-plus")
base_url = os.getenv("OPENAI_BASE_URL", "(未设置，走 OpenAI 官方)")
api_key = os.getenv("OPENAI_API_KEY", "")
key_preview = api_key[:8] + "..." if api_key else "(未设置)"

print(f"模型: {model}")
print(f"BASE_URL: {base_url}")
print(f"API_KEY: {key_preview}")
print("-" * 50)

llm = create_chat_model(model, temperature=0.3)
resp = llm.invoke("请只回复四个字：连接成功")
print(f"✅ 模型回复: {resp.content}")
