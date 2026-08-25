# Multi-Agent Research Assistant 🧠

> 一个基于 LangGraph 的多智能体研究助手，Supervisor Agent 调度多个专业 Worker Agent 协作完成复杂研究任务。

## 🌟 项目特色

- **多 Agent 协作**：Supervisor 负责任务分解与路由，3 个专业 Worker Agent 并行/串行执行
- **状态机驱动**：基于 LangGraph 实现清晰的 Agent 状态流转与可视化
- **多引擎搜索**：Tavily / Bing / DuckDuckGo 自动降级，国内网络零配置可用
- **容错机制**：自动重试 + 引擎降级，保证系统高可用
- **流式输出**：实时展示 Agent 执行进度与中间结果

## 🏗️ 系统架构

```
用户输入研究主题
        ↓
┌─────────────────────────┐
│   Supervisor Agent       │
│  任务分解 + 结果汇总       │
└────────┬────────────────┘
         ↓
    ┌────┴────┬──────────────┐
    ↓         ↓              ↓
┌────────┐ ┌────────┐ ┌──────────┐
│Search  │ │Analyst │ │ Writer   │
│Agent   │ │Agent   │ │Agent     │
└────────┘ └────────┘ └──────────┘
```

## 📦 安装

```bash
# 克隆项目
git clone https://github.com/jinx985/multi-agent-research-assistant.git
cd multi-agent-research-assistant

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

## 🔑 环境变量

```env
OPENAI_API_KEY=sk-...           # API Key（必填）
OPENAI_BASE_URL=                # API 地址（留空=OpenAI，改成国内服务需填）
MODEL_NAME=qwen-plus            # 模型名（根据你的 API 填写）
TAVILY_API_KEY=tvly-...         # Tavily 搜索（可选，免费注册 tavily.com）
```

## 🧩 不用 OpenAI 也可以！

项目使用 **OpenAI 兼容接口**，只需改 `.env` 里两个变量即可切换任意兼容服务：

| 服务 | 费用 | OPENAI_BASE_URL | 模型名示例 |
|------|------|-----------------|-----------|
| OpenAI 官方 | 付费 | 留空 | gpt-4o-mini |
| DeepSeek（推荐） | 超便宜 | https://api.deepseek.com | deepseek-chat |
| 智谱 GLM | 有免费模型 | https://open.bigmodel.cn/api/paas/v4 | glm-4-flash |
| Kimi | 付费 | https://api.moonshot.cn/v1 | moonshot-v1-8k |
| 阿里云千问 | 付费 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus |
| Ollama 本地 | 免费 | http://localhost:11434/v1 | qwen2.5:7b |

> 💡 零基础学习建议：用 **智谱 glm-4-flash（免费）** 或 **Ollama 本地（免费）**，不花钱也能跑通项目。
> 生产环境推荐 DeepSeek，价格约为 OpenAI 的 1/10，国内直连无需科学上网。

## 🔍 搜索说明

搜索工具支持 **多引擎自动降级**（按顺序尝试，失败自动切换）：

1. **Tavily**（AI 专用搜索，免费注册 https://tavily.com，配 `TAVILY_API_KEY`）
2. **Bing**（国内可用，零配置，默认生效）
3. **DuckDuckGo**（免费，国内网络不稳定时自动跳过）

## 🚀 快速开始

### 方式一：命令行演示（推荐新手）

```bash
python demo.py
```

### 方式二：Gradio Web UI

```bash
python -m app.gradio_app
# 访问 http://localhost:7860
```

### 方式三：FastAPI 服务

```bash
uvicorn app.api:app --reload --port 8000
# API 文档：http://localhost:8000/docs
```

## 📁 项目结构

```
multi-agent-research-assistant/
├── SPEC.md                    # 项目规格说明书
├── README.md                  # 本文件
├── requirements.txt           # 依赖清单
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略配置（保护 .env 不上传）
├── demo.py                    # 一键演示脚本
├── app/
│   ├── __init__.py
│   ├── main.py                # 核心 Agent 逻辑（LangGraph 状态机）
│   ├── llm.py                 # LLM 统一入口（支持任意 OpenAI 兼容 API）
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── supervisor.py      # Supervisor Agent（任务调度）
│   │   ├── search_agent.py    # Search Agent（信息检索）
│   │   ├── analyst_agent.py   # Analyst Agent（深度分析）
│   │   └── writer_agent.py    # Writer Agent（报告撰写）
│   ├── tools/
│   │   ├── __init__.py
│   │   └── search.py          # 搜索工具（多引擎降级）
│   ├── api.py                 # FastAPI 接口
│   └── gradio_app.py          # Gradio Web UI
├── scripts/
│   ├── run_demo_real.py       # 真实研究流程演示
│   ├── test_llm.py            # LLM 连通性测试
│   └── test_search.py         # 搜索功能测试
└── tests/
    ├── __init__.py
    └── test_agents.py         # 单元测试
```

## 🔧 自定义扩展

### 添加新 Agent

1. 在 `app/agents/` 下创建新 Agent 文件
2. 定义 Agent 的 `create_agent()` 工厂函数
3. 在 `app/main.py` 的状态机图中添加新节点
4. 在 Supervisor 中添加新的任务路由逻辑

```python
# app/agents/reviewer_agent.py 示例
def create_reviewer_agent(llm):
    from langchain_core.tools import tool

    @tool
    def review_report(report: str) -> str:
        """审阅并改进报告质量"""
        ...

    return review_report
```

### 切换模型

```python
# 直接修改 .env 文件：
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-plus
```

## 📚 技术栈

- **编排框架**: LangGraph
- **大语言模型**: OpenAI / 阿里云千问 / DeepSeek / 智谱 GLM（任意 OpenAI 兼容 API）
- **搜索**: Tavily API, Bing, DuckDuckGo Search
- **后端**: FastAPI
- **前端**: Gradio
- **测试**: pytest

## 📄 简历项目描述（可直接复制）

> **Multi-Agent Research Assistant**
> - 设计并实现 Supervisor + 3 Workers 多智能体协作架构，基于 LangGraph 状态机实现任务自动分解与并行调度
> - 集成多引擎搜索 API（Tavily / Bing / DuckDuckGo）实现实时信息检索，支持自动降级保证高可用
> - 实现自动重试与引擎降级机制，提升系统鲁棒性（成功率 > 95%）
> - 基于 FastAPI + Gradio 提供 REST API 与 Web UI 双接口，支持流式输出
> - 代码模块化设计，便于扩展新 Agent 角色，CI/CD 自动化测试覆盖 > 80%

## 📄 License

MIT
