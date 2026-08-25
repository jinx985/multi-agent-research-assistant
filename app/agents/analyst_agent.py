# app/agents/analyst_agent.py
"""
Analyst Agent — 数据分析专家
对搜索结果进行深度分析，提取关键洞察
"""

from langchain_openai import ChatOpenAI

from ..llm import create_chat_model


def create_analyst_agent(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    """
    创建 Analyst Agent
    
    Analyst 的职责：
    1. 理解搜索结果的内容
    2. 识别关键数据、事实、观点
    3. 分析不同来源的一致性和矛盾点
    4. 提炼核心洞察（insights）
    """
    llm = create_chat_model(model_name, temperature=0.2)
    return llm


def analyst_node(state: dict, llm: ChatOpenAI) -> dict:
    """
    Analyst Agent 的执行节点
    """
    topic = state.get("topic", "")
    search_results = state.get("search_results", "")
    
    state.setdefault("retry_count", {})
    state.setdefault("errors", {})
    
    prompt = f"""你是一个专业的研究分析师，擅长从大量信息中提炼关键洞察。

## 研究主题
{topic}

## 搜索结果
{search_results}

## 你的任务
请对以上搜索结果进行深度分析，输出以下内容：

### 核心发现（Key Findings）
列出 3-5 个最重要的发现或事实。

### 关键数据点
如果有具体数据（百分比、年份、数字），请特别列出。

### 一致性分析
不同来源是否达成共识？有没有相互矛盾的观点？

### 争议与不确定性
有哪些问题尚无定论？有哪些观点存在争议？

### 深层洞察
基于以上分析，你能提炼出哪些深层洞察？

请用结构化、专业的语言输出分析结果。"""
    
    try:
        response = llm.invoke(prompt)
        state["analysis"] = str(response.content)
        state["current_step"] = "writer"
        
    except Exception as e:
        state["errors"]["analyst"] = str(e)
        state["retry_count"]["analyst"] = state["retry_count"].get("analyst", 0) + 1
        
        if state["retry_count"]["analyst"] < 3:
            state["current_step"] = "analyst"  # 重试
        else:
            state["analysis"] = f"[分析不可用] {str(e)}"
            state["current_step"] = "writer"
    
    return state
