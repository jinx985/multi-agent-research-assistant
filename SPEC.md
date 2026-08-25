# Multi-Agent Research Assistant — 项目规格说明书

## 1. 项目概述

**项目名称**：Multi-Agent Research Assistant（多智能体研究助手）  
**类型**：AI Agent 应用 / LLM 工程  
**一句话描述**：Supervisor Agent 调度多个专业 Worker Agent协作完成复杂研究任务，并自动生成结构化报告。

---

## 2. 系统架构

```
用户输入研究主题
        ↓
┌─────────────────────────┐
│   Supervisor Agent       │  ← 任务分解 + 结果汇总
│  (任务规划 & 路由)        │
└────────┬────────────────┘
         ↓ 分解为子任务
    ┌────┴────┬──────────────┐
    ↓         ↓              ↓
┌────────┐ ┌────────┐ ┌──────────┐
│ Search │ │Analyst │ │ Writer   │
│ Agent  │ │ Agent  │ │ Agent    │
└───┬────┘ └───┬────┘ └────┬─────┘
    ↓          ↓           ↓
 搜索结果   分析结果    草稿文本
    └──────────┴──────────┘
              ↓
        Supervisor 整合 + 最终报告
```

### 3 个 Worker Agent 职责

| Agent | 角色 | 工具/能力 |
|-------|------|---------|
| **Search Agent** | 信息检索专家 | Tavily / DuckDuckGo 搜索、结果摘要 |
| **Analyst Agent** | 数据分析专家 | 数据结构化、关键洞察提取、逻辑验证 |
| **Writer Agent** | 内容撰写专家 | Markdown 报告生成、排版润色 |

---

## 3. 核心功能

### F1: 任务自动分解
- 用户输入模糊研究主题（如"AI对教育的影响"）
- Supervisor 自动拆解为具体子任务，分发给对应 Agent

### F2: 并行 + 串行混合执行
- 相互独立的子任务并行执行（搜索 + 分析可同时）
- 存在依赖关系的串行执行（先搜后分析）

### F3: 结果聚合与报告生成
- Supervisor 收集所有 Agent 输出，汇总为结构化 Markdown 报告
- 支持报告大纲预览、修改意见反馈

### F4: 错误重试机制
- 单个 Agent 执行失败时自动重试（最多3次）
- 重试失败时优雅降级，不阻塞整体流程

---

## 4. 技术栈

| 层级 | 技术选型 |
|------|---------|
| 框架 | LangGraph（状态机驱动的多 Agent 编排）|
| LLM | OpenAI GPT-4o-mini / Claude 3.5 Haiku |
| 搜索 | Tavily API / DuckDuckGo（免费） |
| 后端 | FastAPI（可选 REST 接口） |
| 前端 | Gradio（可选 demo UI） |
| 部署 | Docker / Railway / Vercel |

---

## 5. 开发阶段

### Phase 1（零基础上手）：核心跑通
- 单 Agent Chain-of-Thought 推理流程
- 手动定义任务节点，固定路由

### Phase 2（进阶）：多 Agent 协作
- Supervisor + Workers 完整架构
- LangGraph 状态机实现任务分发

### Phase 3（扩展）：工程化增强
- 添加 RAG 知识库检索增强
- 添加长期记忆（Vector DB）
- 添加流式输出（Streaming）
- Docker 容器化部署

---

## 6. 简历关键词（可直接引用）

```
项目名称：Multi-Agent Research Assistant
技术栈：LangGraph / LangChain · Python · FastAPI · OpenAI API
核心工作：
  - 设计并实现 Supervisor + Workers 多智能体协作架构
  - 基于状态机实现任务自动分解、并行调度与结果聚合
  - 集成搜索 API 实现实时信息检索与结构化报告生成
  - 添加错误重试与优雅降级，提升系统鲁棒性
  - （进阶）引入 RAG + Vector DB 实现知识库增强检索
项目亮点：
  - 完整走通 LLM 应用开发全链路：需求 → 设计 → 实现 → 部署
  - 体现对 Agent 架构（规划/记忆/工具调用）的深入理解
  - 代码模块化设计，便于扩展新 Agent 角色
```
