# app/main.py
"""
Multi-Agent Research Assistant — 核心编排引擎
基于 LangGraph 状态机实现多 Agent 协作流程
"""

import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

from .agents.supervisor import ResearchState, supervisor_node, should_continue, create_supervisor_agent
from .agents.search_agent import create_search_agent, search_node
from .agents.analyst_agent import create_analyst_agent, analyst_node
from .agents.writer_agent import create_writer_agent, writer_node

# 加载 .env 环境变量
load_dotenv()

# 默认模型名（可通过环境变量 MODEL_NAME 覆盖）
DEFAULT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


# ---------------------------------------------------------------------------
# LangGraph 状态机构建
# ---------------------------------------------------------------------------

def build_research_graph(model_name: str | None = None):
    """
    构建多 Agent 协作的 LangGraph 状态机
    
    流程：
    supervisor → search → analyst → writer → supervisor(汇总) → END
    """
    
    # 创建各 Agent 的 LLM 实例
    model_name = model_name or DEFAULT_MODEL
    supervisor_llm = create_supervisor_agent(model_name)
    search_llm = create_search_agent(model_name)
    analyst_llm = create_analyst_agent(model_name)
    writer_llm = create_writer_agent(model_name)
    
    # 定义节点
    nodes = {
        "supervisor": lambda state: supervisor_node(state, supervisor_llm),
        "search": lambda state: search_node(state, search_llm),
        "analyst": lambda state: analyst_node(state, analyst_llm),
        "writer": lambda state: writer_node(state, writer_llm),
    }
    
    # 构建状态图
    workflow = StateGraph(ResearchState)
    
    # 添加节点
    workflow.add_node("supervisor", nodes["supervisor"])
    workflow.add_node("search", nodes["search"])
    workflow.add_node("analyst", nodes["analyst"])
    workflow.add_node("writer", nodes["writer"])
    
    # 设置入口
    workflow.set_entry_point("supervisor")
    
    # 添加边（路由）
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "search": "search",
            "analyst": "analyst",
            "writer": "writer",
            "done": END,
        }
    )
    
    # 普通边
    workflow.add_edge("search", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("writer", END)
    
    # 编译图（添加内存检查点，支持断点续跑）
    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph


# ---------------------------------------------------------------------------
# 主入口函数
# ---------------------------------------------------------------------------

def run_research(topic: str, model_name: str | None = None, stream: bool = True):
    """
    运行研究任务
    
    Args:
        topic: 研究主题
        model_name: 使用的模型（默认读环境变量 MODEL_NAME）
        stream: 是否流式输出
    
    Returns:
        最终状态（包含 report 字段）
    """
    model_name = model_name or DEFAULT_MODEL
    graph = build_research_graph(model_name)
    
    # 初始化状态
    initial_state: ResearchState = {
        "topic": topic,
        "sub_tasks": [],
        "search_results": "",
        "analysis": "",
        "report": "",
        "current_step": "search",
        "retry_count": {},
        "errors": {},
    }
    
    # 执行图（带 thread_id，配合 MemorySaver 检查点）
    config = {
        "configurable": {"thread_id": "research-1"},
        "recursion_limit": 50,
    }
    if stream:
        # 流式输出：实时展示每个节点的执行结果
        for event in graph.stream(initial_state, config=config):
            node_name = list(event.keys())[0]
            node_state = event[node_name]
            
            if node_name == "supervisor":
                step = node_state.get("current_step", "")
                print(f"\n📋 [Supervisor] 下一步: {step}")
            elif node_name == "search":
                results = node_state.get("search_results", "")
                if results:
                    print(f"\n🔍 [Search] 完成，摘要：{results[:100]}...")
            elif node_name == "analyst":
                analysis = node_state.get("analysis", "")
                if analysis:
                    print(f"\n📊 [Analyst] 完成，洞察数：{analysis.count('###')}")
            elif node_name == "writer":
                report = node_state.get("report", "")
                if report:
                    print(f"\n✍️  [Writer] 完成，报告字数：{len(report)}")
        
        # 获取最终状态
        final_state = graph.invoke(initial_state, config=config)
    else:
        final_state = graph.invoke(initial_state, config=config)
    
    return final_state


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Research Assistant")
    parser.add_argument("--topic", "-t", type=str, help="研究主题")
    parser.add_argument("--model", "-m", type=str, default=None, help="模型名称（默认读环境变量 MODEL_NAME）")
    args = parser.parse_args()
    
    topic = args.topic or input("请输入研究主题：")
    
    print(f"\n🚀 开始研究：{topic}\n")
    result = run_research(topic, args.model, stream=True)
    
    print("\n" + "=" * 60)
    print("📄 最终报告")
    print("=" * 60)
    print(result.get("report", "（无报告）"))
