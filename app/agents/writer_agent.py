# app/agents/writer_agent.py
"""
Writer Agent — 内容撰写专家
基于分析结果生成结构化的研究报告
"""

from langchain_openai import ChatOpenAI

from ..llm import create_chat_model


def create_writer_agent(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    """
    创建 Writer Agent
    
    Writer 的职责：
    1. 整合 Supervisor + Analyst 的输出
    2. 生成结构化、专业的 Markdown 报告
    3. 确保报告逻辑清晰、可读性强
    """
    llm = create_chat_model(model_name, temperature=0.4)
    return llm


def writer_node(state: dict, llm: ChatOpenAI) -> dict:
    """
    Writer Agent 的执行节点
    """
    topic = state.get("topic", "")
    search_results = state.get("search_results", "")
    analysis = state.get("analysis", "")
    
    state.setdefault("retry_count", {})
    state.setdefault("errors", {})
    
    prompt = f"""你是一个专业的技术写作专家，擅长将复杂的研究内容整理成结构清晰、阅读友好的报告。

## 研究主题
{topic}

## 信息来源
### 搜索结果摘要
{search_results[:2000] if search_results else "（无搜索结果）"}

### 分析师洞察
{analysis if analysis else "（无分析结果）"}

## 你的任务
请基于以上内容，生成一份完整的研究报告，要求：

### 格式要求
- 使用 Markdown 格式
- 包含清晰的标题层级
- 适当使用表格、列表增强可读性
- 总字数 800-1500 字

### 内容结构
1. **摘要**（Executive Summary）：一句话概括研究主题的核心结论
2. **背景介绍**：研究主题的背景和重要性
3. **核心发现**：3-5 个最重要的发现
4. **深度分析**：关键数据的详细解读
5. **趋势与展望**：未来发展方向或影响
6. **参考资料**：信息来源（可标注"基于网络搜索"）

### 写作风格
- 客观、专业，避免过多主观臆断
- 数据说话，用具体事实支撑论点
- 逻辑连贯，段落之间有清晰的承接关系

请直接输出报告内容（Markdown 格式）："""
    
    try:
        response = llm.invoke(prompt)
        state["report"] = str(response.content)
        state["current_step"] = "done"
        
    except Exception as e:
        state["errors"]["writer"] = str(e)
        state["retry_count"]["writer"] = state["retry_count"].get("writer", 0) + 1
        
        if state["retry_count"]["writer"] < 3:
            state["current_step"] = "writer"  # 重试
        else:
            state["report"] = f"[报告生成失败] {str(e)}"
            state["current_step"] = "done"
    
    return state
