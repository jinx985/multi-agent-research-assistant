# app/agents/search_agent.py
"""
Search Agent — 信息检索专家
使用多引擎搜索（Tavily / Bing / DuckDuckGo 自动降级）
"""

from langchain_openai import ChatOpenAI

from ..llm import create_chat_model
from ..tools.search import web_search


# ---------------------------------------------------------------------------
# Agent 工厂
# ---------------------------------------------------------------------------

def create_search_agent(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    """
    创建 Search Agent
    
    Search Agent 的职责：
    1. 接收 Supervisor 分配的搜索任务
    2. 生成高质量搜索关键词（query）
    3. 执行搜索并整理结果
    """
    llm = create_chat_model(model_name, temperature=0.2)
    
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools([web_search])
    
    return llm_with_tools


def search_node(state: dict, llm: ChatOpenAI) -> dict:
    """
    Search Agent 的执行节点
    """
    topic = state.get("topic", "")
    state.setdefault("retry_count", {})
    state.setdefault("errors", {})
    
    prompt = f"""你是一个专业的信息检索专家。
研究主题：{topic}

请执行以下步骤：
1. 生成 2-3 个高质量搜索关键词（覆盖不同角度）
2. 使用 web_search 工具进行搜索
3. 整理搜索结果，返回结构化的信息摘要

开始执行："""
    
    try:
        response = llm.invoke(prompt)
        
        # 如果 LLM 调用的工具，这里处理工具调用结果
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results = []
            for tc in response.tool_calls:
                if tc["name"] == "web_search":
                    result = web_search.invoke(tc["args"])
                    tool_results.append(result)
            state["search_results"] = "\n---\n".join(tool_results)
        else:
            state["search_results"] = str(response.content)
        
        state["current_step"] = "analyst"
        
    except Exception as e:
        state["errors"]["search"] = str(e)
        state["retry_count"]["search"] = state["retry_count"].get("search", 0) + 1
        
        # 重试逻辑：最多3次（使用多引擎搜索）
        if state["retry_count"]["search"] < 3:
            state["search_results"] = web_search.invoke({"query": topic})
        else:
            state["search_results"] = f"[搜索不可用] {str(e)}"
            state["current_step"] = "analyst"
    
    return state
