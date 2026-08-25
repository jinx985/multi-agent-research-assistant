# app/llm.py
"""
统一的模型创建模块

支持通过环境变量切换任意 OpenAI 兼容 API：
- OpenAI 官方：OPENAI_API_KEY=sk-xxx（默认）
- DeepSeek：  OPENAI_BASE_URL=https://api.deepseek.com
- 智谱 GLM：  OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
- Kimi：      OPENAI_BASE_URL=https://api.moonshot.cn/v1
- 通义千问：  OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
- Ollama 本地：OPENAI_BASE_URL=http://localhost:11434/v1（不需要真实 Key）
"""

import os
from langchain_openai import ChatOpenAI


def create_chat_model(model_name: str, temperature: float = 0.3) -> ChatOpenAI:
    """
    创建 ChatOpenAI 实例

    Args:
        model_name: 模型名称（如 gpt-4o-mini / deepseek-chat / glm-4-flash）
        temperature: 随机性（0=严谨，1=发散）

    环境变量:
        OPENAI_BASE_URL: API 地址（不填则用 OpenAI 官方）
        OPENAI_API_KEY:  API Key（本地模型可填任意值）
    """
    base_url = os.getenv("OPENAI_BASE_URL") or None
    api_key = os.getenv("OPENAI_API_KEY") or "EMPTY"  # 本地模型时任意值即可

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
    )
