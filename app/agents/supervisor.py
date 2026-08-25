# app/agents/supervisor.py
"""
Supervisor Agent — 任务规划者
负责任务分解 + 路由决策 + 结果聚合
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from ..llm import create_chat_model


class ResearchState(TypedDict, total=False):
    """贯穿整个 Agent 流程的共享状态"""
    topic: str                        # 用户研究主题
    sub_tasks: list[str]              # 分解后的子任务列表
    search_results: str               # Search Agent 返回结果
    analysis: str                      # Analyst Agent 分析结果
    report: str                        # Writer Agent 生成报告
    current_step: str                  # 当前执行步骤
    retry_count: dict[str, int]        # 各 Agent 重试计数
    errors: dict[str, str]             # 各 Agent 错误信息


def create_supervisor_agent(model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    """
    创建 Supervisor Agent 的 LLM 实例
    
    Supervisor 的核心能力：
    1. 理解用户模糊需求 → 拆解为具体子任务
    2. 判断当前应该调度哪个 Worker
    3. 汇总所有 Worker 结果 → 生成最终报告
    """
    llm = create_chat_model(model_name, temperature=0.3)
    
    # Supervisor 的系统提示词
    supervisor_prompt = """你是一个研究任务规划专家（Supervisor）。
给定一个研究主题，你需要：
1. 将主题分解为 2-4 个具体的子任务
2. 判断子任务之间的依赖关系（哪些可以并行，哪些必须串行）
3. 按顺序输出子任务列表

当前状态：
- 研究主题：{topic}
- 已完成任务：{completed}

请输出：
## 任务分解
1. [任务1名称]: [任务描述]
2. [任务2名称]: [任务描述]
...

## 执行计划
[并行/串行说明]
"""
    
    return llm


def supervisor_node(state: ResearchState, llm: ChatOpenAI) -> ResearchState:
    """
    Supervisor 的执行节点
    在 LangGraph 状态机中，每个节点都是一个函数
    """
    topic = state.get("topic", "")
    search_done = bool(state.get("search_results"))
    analyst_done = bool(state.get("analysis"))
    writer_done = bool(state.get("report"))
    
    completed = []
    if search_done:
        completed.append("Search（搜索）")
    if analyst_done:
        completed.append("Analyst（分析）")
    if writer_done:
        completed.append("Writer（撰写）")
    
    prompt = f"""研究主题：{topic}
已完成：{', '.join(completed) if completed else '无'}"""
    
    response = llm.invoke(prompt)
    
    # 判断下一步
    if not search_done:
        state["current_step"] = "search"
    elif not analyst_done:
        state["current_step"] = "analyst"
    elif not writer_done:
        state["current_step"] = "writer"
    else:
        state["current_step"] = "done"
    
    return state


def should_continue(state: ResearchState) -> str:
    """路由决策：判断下一步走哪个 Agent"""
    step = state.get("current_step", "search")
    return step
