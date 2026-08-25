# Multi-Agent Research Assistant — 学习指南（零基础版）

> 本文档配套项目代码，逐文件讲解 + 面试问答 + 学习路线。
> 阅读方式：打开代码文件对照着看，效果最好。

---

## 第一部分：每个文件是干什么的

### 🗺️ 先看整体地图

```
multi-agent-research-assistant/
├── README.md                    ← 📖 项目说明书（给陌生人看的门面）
├── SPEC.md                      ← 📐 设计图纸（当初怎么设计的）
├── requirements.txt             ← 📦 购物清单（要装哪些库）
├── .env.example                 ← 🔑 钥匙模板（API Key 放哪）
├── demo.py                      ← 🎬 宣传片（一键演示，不用真 API）
├── app/
│   ├── main.py                  ← ⚙️ 传送带（把所有 Agent 串起来）
│   ├── api.py                   ← 📡 电话总机（HTTP 接口）
│   ├── gradio_app.py            ← 🖥️ 前台（网页界面）
│   ├── agents/
│   │   ├── supervisor.py        ← 👔 项目经理
│   │   ├── search_agent.py      ← 🔍 资料员
│   │   ├── analyst_agent.py     ← 📊 分析师
│   │   └── writer_agent.py      ← ✍️ 撰稿人
│   └── tools/
│       └── search.py            ← 🛠️ 资料员的"搜索工具"
└── tests/
    └── test_agents.py           ← 🧪 质检员（自动检查代码对不对）
```

---

### 📖 根目录文件（4 个）

| 文件 | 大白话 | 什么时候看 |
|------|--------|-----------|
| `README.md` | 项目的"门面"，告诉别人这是啥、怎么装、怎么跑 | 面试前必背，简历描述直接抄这里 |
| `SPEC.md` | 项目的"设计图纸"，记录架构和功能设计 | 想深入了解设计思路时看 |
| `requirements.txt` | "购物清单"，`pip install -r requirements.txt` 会照着它装库 | 换电脑/部署时用 |
| `.env.example` | "钥匙模板"，复制成 `.env` 后填入你的 API Key | 第一次配置时用 |

> 💡 `.env` 文件：存放密钥的地方（如 OPENAI_API_KEY），**永远不要提交到 GitHub**。
> 所以项目里只有 `.env.example`（模板），没有 `.env`（你的真实钥匙）。

---

### ⚙️ app/main.py — 传送带（最重要！）

**大白话**：这个文件是整条流水线。它做了 3 件事：

1. **造人**：调用 4 个 agent 文件里的"工厂函数"，创建 4 个 AI 员工
2. **搭流水线**：用 LangGraph 把 4 个人按顺序连起来（状态机）
3. **喊开工**：`run_research(topic)` 输入主题，跑完整条流水线，返回报告

**核心代码逐段拆解：**

```python
workflow = StateGraph(ResearchState)   # 1. 建一个"流水线图纸"
workflow.add_node("supervisor", ...)   # 2. 把 4 个员工放进流水线
workflow.add_node("search", ...)
workflow.add_node("analyst", ...)
workflow.add_node("writer", ...)

workflow.set_entry_point("supervisor") # 3. 从项目经理开始干活

# 4. 项目经理干完活后，根据情况决定下一个派谁
workflow.add_conditional_edges(
    "supervisor",
    should_continue,                   # 看"当前该谁干活"这个标志
    {"search": "search", ...}
)
```

**关键概念：State（状态）**

```python
class ResearchState(TypedDict, total=False):
    topic: str          # 用户输入的主题
    search_results: str # 搜索到的资料（资料员填）
    analysis: str       # 分析结果（分析师填）
    report: str         # 最终报告（撰稿人填）
```

> 💡 State 就像一块"共享白板"：每个 Agent 干完活，把结果写到白板上，
> 下一个 Agent 从白板上读数据继续干活。这就是多 Agent 协作的本质。

**面试常问：LangGraph 是什么？**
> 一个 Python 库，用来构建"图状"的 AI 流程。节点（node）= 一个处理步骤，
> 边（edge）= 步骤之间的流转，条件边（conditional edge）= 根据状态决定下一步走哪。
> 比传统 if-else 链更灵活、可视化、支持断点续跑。

---

### 👔 app/agents/supervisor.py — 项目经理

**大白话**：负责"接需求、拆任务、派活、汇总"。

文件里有 3 个东西：

| 代码 | 作用 |
|------|------|
| `ResearchState` | 共享白板的"设计图纸"（定义有哪些字段） |
| `create_supervisor_agent()` | 造项目经理的"工厂函数"（返回一个 AI 模型实例） |
| `supervisor_node()` | 项目经理的"干活逻辑"：看白板上缺什么 → 决定派谁 |
| `should_continue()` | 路由函数：返回 "search"/"analyst"/"writer"/"done" |

**核心逻辑（supervisor_node）：**

```python
if not search_done:      # 资料还没搜 → 派资料员
    state["current_step"] = "search"
elif not analyst_done:   # 搜完了没分析 → 派分析师
    state["current_step"] = "analyst"
elif not writer_done:    # 分析完了没写稿 → 派撰稿人
    state["current_step"] = "writer"
else:                    # 都干完了 → 结束
    state["current_step"] = "done"
```

> 💡 这就是"规划（Planning）"：Agent 的核心能力之一。
> 面试时说"Supervisor 负责任务分解和路由决策"就是指这段代码。

---

### 🔍 app/agents/search_agent.py — 资料员

**大白话**：负责上网搜资料。文件里有 2 个部分：

**① 工具（Tool）：**

```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    # 用 duckduckgo_search 库去搜索引擎查
    # 把结果整理成"标题+链接+摘要"的文本
```

> 💡 这是 Agent 的"工具调用（Tool Use）"能力：AI 不会自己上网，
> 它通过调用这个函数来"长出上网的手"。

**② 干活逻辑（search_node）：**

```python
# 让 AI 根据主题生成搜索关键词 → 调用 web_search → 结果存到白板
state["search_results"] = 搜索结果
state["current_step"] = "analyst"   # 干完活告诉项目经理：该分析师了
```

**还藏了一个亮点：容错（重试机制）**

```python
try:
    ... 正常搜索
except Exception as e:
    if 重试次数 < 3:
        再试一次
    else:
        降级处理，不阻塞流程
```

> 💡 面试必讲："我给每个 Agent 加了自动重试（最多3次）和优雅降级，
> 单个 Agent 挂了不影响整条流水线。" 这就是鲁棒性（Robustness）。

---

### 📊 app/agents/analyst_agent.py — 分析师

**大白话**：把搜来的资料提炼成"核心发现、关键数据、争议点"。

文件很短，就 2 个函数：

```python
create_analyst_agent(model)   # 工厂函数：造一个分析师 AI
analyst_node(state, llm)      # 干活逻辑：把搜索结果 + 分析指令拼成提示词
                              # → 让 AI 输出结构化分析 → 存到白板
```

**核心是提示词（Prompt）**——文件里那段长长的中文就是：

```
你是专业的研究分析师...
### 核心发现（Key Findings）
### 关键数据点
### 一致性分析
### 深层洞察
```

> 💡 这就是 Prompt Engineering：AI 的输出质量 = 你给它的指令质量。
> 用"角色设定 + 明确结构"能让 AI 输出稳定、专业。
> 面试讲："我通过结构化提示词让分析结果稳定输出 5 个固定板块。"

---

### ✍️ app/agents/writer_agent.py — 撰稿人

**大白话**：把分析结果写成一篇漂亮的 Markdown 报告。

和分析师结构几乎一样，区别只在**提示词**：

```
你是专业的技术写作专家...
要求：800-1500字、Markdown 格式、包含摘要/背景/核心发现/深度分析/趋势展望/参考资料
```

> 💡 三个 Worker 的文件结构其实是**同一个模式**：
>
> ```
> 工厂函数（造人）+ 节点函数（干活）
> 干活 = 拼提示词 → 调 AI → 结果写白板 → 更新 current_step
> ```
>
> 看懂这一个模式，3 个 agent 文件就都懂了。

---

### 📡 app/api.py — 电话总机（FastAPI）

**大白话**：让别的地方（网页、手机 App、其他服务）能通过 HTTP 请求调用你的流水线。

```python
@app.post("/research")          # 别人 POST 一个主题过来
async def research(request):
    result = await asyncio.to_thread(run_research, ...)  # 调传送带
    return ResearchResponse(...)                          # 返回报告
```

> 💡 面试讲："我提供了 REST API 接口（FastAPI），支持 JSON 请求/响应，
> 可以对接前端或移动端。用 `asyncio.to_thread` 把耗时任务丢到线程池，避免阻塞事件循环。"

---

### 🖥️ app/gradio_app.py — 前台（Web UI）

**大白话**：一个长得像聊天工具的网页界面，在浏览器里输入主题 → 点按钮 → 看报告。

```python
with gr.Blocks():
    topic_input = gr.Textbox(...)       # 输入框
    submit_btn = gr.Button("开始研究")   # 按钮
    final_output = gr.Markdown(...)     # 结果显示区
    submit_btn.click(fn=research_with_ui, inputs=[...], outputs=[...])
```

> 💡 Gradio 是给 AI 应用做 Demo 界面的最流行工具，几行代码就能出一个漂亮界面。
> 面试讲："我用 Gradio 做了可视化界面，可以实时看到每个 Agent 的执行过程。"

---

### 🛠️ app/tools/search.py — 工具箱

**大白话**：搜索工具的"独立版本"，和 search_agent.py 里的 web_search 是同一个东西，抽出来单独放（避免重复代码）。

> 💡 这是工程化思维：工具层和 Agent 层分离，以后想换 Tavily 搜索引擎，
> 只改这一个文件就行。

---

### 🧪 tests/test_agents.py — 质检员

**大白话**：自动检查代码有没有写错的测试文件。

```python
def test_should_continue(self):
    assert should_continue({"current_step": "search"}) == "search"
    assert should_continue({"current_step": "done"}) == "done"
```

> 💡 面试讲："我写了单元测试（pytest），覆盖路由决策、Agent 创建、
> 搜索工具（mock 掉网络），保证核心逻辑不回归。"
> **加分项**：零基础候选人写测试，说明有工程意识，非常加分！

---

### 🎬 demo.py — 宣传片

**大白话**：不花一分钱 API 费用，也能演示整个流程的脚本。
里面写死了演示数据（模拟搜索结果、模拟报告），让零基础的人先看懂"这个项目是干嘛的"。

```bash
python demo.py   # 直接跑，看到完整流程演示
```

---

## 第二部分：面试问答（背下来！）

### Q1: 介绍一下你的项目？

**回答模板（30秒版）：**
> "我做了一个多智能体研究助手。用户输入一个研究主题，系统会自动调度
> Supervisor、Search、Analyst、Writer 四个 Agent 协作完成研究。
> Supervisor 负责任务分解和路由决策，Search Agent 调用搜索引擎收集资料，
> Analyst Agent 提炼关键洞察，Writer Agent 生成结构化 Markdown 报告。
> 整个流程用 LangGraph 状态机编排，我提供了 FastAPI 和 Gradio 两个接口，
> 还实现了错误重试和优雅降级。"

**为什么这么答**：先讲"是什么"（一句话），再讲"怎么协作"（4个角色），
最后讲"技术亮点"（LangGraph + 双接口 + 容错）。逻辑清晰，面试官好追问。

### Q2: 什么是多 Agent？为什么不用一个 Agent 搞定？

**回答模板：**
> "单 Agent 就像一个人干所有事：又要搜索、又要分析、又要写报告，
> 上下文容易混乱，角色目标不清晰。多 Agent 把大任务拆成小任务，
> 每个 Agent 有明确的角色和提示词，各干各的专长，质量更高。
> 就像公司分工，项目经理、资料员、分析师、撰稿人各司其职。"

### Q3: LangGraph 和 LangChain 的区别？

**回答模板：**
> "LangChain 是一套 LLM 应用开发的工具库，提供模型封装、提示词管理、工具调用等。
> LangGraph 是基于 LangChain 的**状态机编排框架**，适合构建复杂的、有循环和条件分支的多 Agent 流程。
> 我的项目里，LangChain 负责'单个 Agent 怎么干活'（模型、工具、提示词），
> LangGraph 负责'多个 Agent 怎么协作'（节点、边、状态流转）。"

### Q4: Agent 的核心能力有哪些？你的项目体现了哪些？

**回答模板：**
> "Agent 的核心能力一般指：**规划（Planning）、记忆（Memory）、工具调用（Tool Use）、反思（Reflection）**。
> 我的项目体现了：
> - 规划：Supervisor 的任务分解和路由决策
> - 工具调用：Search Agent 调用 web_search 工具
> - 记忆：LangGraph 的 State 作为短期记忆，Agent 之间共享上下文
> - 反思：Analyst 会对搜索结果做一致性分析（发现矛盾点）
> - 未来可以加长期记忆（向量数据库）和反思循环（Critic Agent）"

### Q5: 你的 State 是怎么设计的？为什么？

**回答模板：**
> "State 我用 TypedDict 定义，是贯穿整个流程的共享白板。
> 字段有 topic（主题）、search_results、analysis、report 和 current_step（当前步骤）。
> 每个 Agent 只负责填充自己相关的字段，然后通过 current_step 告诉路由该派谁。
> 这样设计的好处：一是解耦，每个 Agent 不关心别人的内部逻辑；
> 二是可追踪，任何一步的状态都能看到，方便调试和断点续跑。"

### Q6: 怎么保证系统稳定？出错了怎么办？

**回答模板：**
> "我在每个 Agent 节点都加了 try-except 容错：
> 1. 出错时记录错误信息和重试次数（存到 State）
> 2. 重试次数小于 3 次就重跑；超过 3 次就降级（比如搜索失败就用本地模拟数据），
> 3. 保证单点故障不会阻塞整条流水线。
> 另外还用 pytest 写了单元测试，mock 掉网络请求，保证路由逻辑正确。"

### Q7: 怎么部署上线？

**回答模板：**
> "目前项目支持两种方式：
> 1. FastAPI + uvicorn 提供 REST API，可以部署到云服务器或 Railway/Vercel
> 2. 可以写 Dockerfile 容器化（我下一步计划），一条命令启动整个服务
> 3. 密钥管理用 .env + python-dotenv，不上传到代码仓库
> 如果面的是全栈岗，我会强调：前端用 Gradio/React 展示，后端 FastAPI 提供接口，
> 中间用 HTTP 通信，数据存 SQLite/向量库。"

### Q8: 为什么用 DuckDuckGo 不用 Tavily？（延伸问题）

**回答模板：**
> "DuckDuckGo 免费、无需 API Key，适合学习和 demo。Tavily 是专门为 LLM 优化的
> 搜索 API，返回结果更干净、支持摘要抽取，生产环境我会切换过去。
> 我的工具层已经做了封装（app/tools/search.py），换搜索引擎只改一个文件。"

### Q9: 你遇到了什么困难？怎么解决的？（高频！）

**回答模板：**
> "遇到最大的困难是：刚开始用 LangGraph 时，对 State 的更新和条件路由理解不透彻，
> 经常出现 Agent 顺序错乱。解决方法是：
> 1. 先把流程图画在纸上，明确每个节点输入输出
> 2. 用 LangGraph 的调试工具看每一步 State 变化
> 3. 最后用单元测试把路由逻辑固定下来
> 这个经历让我深刻理解了状态机设计，也养成了'先设计再编码'的习惯。"

### Q10: 未来怎么改进这个项目？

**回答模板（体现思考深度）：**
> "三个方向：
> 1. **记忆增强**：加向量数据库（ChromaDB/FAISS），支持多轮对话记忆和知识库检索（RAG）
> 2. **反思循环**：加一个 Critic Agent 审核报告质量，不合格就退回重写
> 3. **工程化**：Docker 部署、日志监控（LangSmith）、并发任务队列（Celery）"

---

## 第三部分：学习路线（4 周计划）

> 目标：从"看不懂"到"能讲明白 + 能改代码 + 面试能答"

### 🗓️ 第 1 周：跑起来 + 看懂流程

| 天 | 任务 | 完成标准 |
|----|------|---------|
| D1 | 跑 `python demo.py`，看模拟演示 | 能说出 4 个 Agent 各干什么 |
| D2 | 通读 `README.md` + `SPEC.md` | 能画出项目架构图 |
| D3 | 安装依赖 + 配置 .env + 跑真实版 | 能跑通一次真实研究 |
| D4 | 读 `app/main.py`（传送带） | 能说出 StateGraph 的节点和边 |
| D5 | 读 `supervisor.py` | 能说出路由逻辑（if-else 链） |
| D6 | 读 3 个 worker 文件 | 发现它们"同一个模式" |
| D7 | 复习 + 写一篇学习笔记 | 能不看代码讲出整体流程 |

**第 1 周重点**：理解"共享白板（State）"和"路由"这两个核心概念。

### 🗓️ 第 2 周：动手改代码

| 任务 | 说明 |
|------|------|
| 改提示词 | 把 writer 的提示词改成"报告要 500 字"，观察输出变化 |
| 改路由 | 给 supervisor 加一个分支：如果主题包含"代码"，先走 analyst |
| 加一个 Agent | 复制 writer_agent.py 改成 "reviewer_agent.py"（审稿人），插到 writer 后面 |
| 写测试 | 给新加的 Agent 写测试用例 |
| 跑 API | `uvicorn app.api:app --reload`，用浏览器访问 /docs 试接口 |
| 跑 UI | `python -m app.gradio_app`，在网页里体验 |

**第 2 周重点**：改代码是最快的学习方式。改坏了再改回来，不怕。

### 🗓️ 第 3 周：深挖概念（面试储备）

| 主题 | 学什么 | 对应面试题 |
|------|--------|-----------|
| Agent 是什么 | ReAct 模式（Reasoning + Acting） | Q4 |
| LangChain | 模型封装、PromptTemplate、Tool | Q3 |
| LangGraph | StateGraph、节点、边、checkpointer | Q5 |
| RAG | 向量检索 + 生成（知识库问答） | Q10 |
| 容错设计 | 重试、降级、超时 | Q6 |

**推荐资料**：
- LangChain 官方文档（有中文版教程）
- B站搜"LangGraph 教程"，选播放量高的
- 吴恩达《Building Systems with the ChatGPT API》免费课（Agent 思想启蒙）

### 🗓️ 第 4 周：面试冲刺

| 任务 | 说明 |
|------|------|
| 背诵 Q1-Q10 回答模板 | 用自己的话讲，不要死记硬背 |
| 做项目复盘 | 列出"我做了什么决策、为什么、踩了什么坑" |
| 准备 1 分钟自我介绍 | 项目版本：是什么 + 亮点 + 成果 |
| 补充简历 | 用 README 里的模板，突出 Agent 架构和工程化 |
| 模拟面试 | 让我（或朋友）扮演面试官随机提问 |

---

## 附录：10 个必懂名词（大白话版）

| 名词 | 大白话 | 面试怎么说 |
|------|--------|-----------|
| Agent | 能"想+做"的 AI 程序：想（推理）→ 做（调用工具/行动） | "具备规划和工具调用能力的 AI 实体" |
| Multi-Agent | 多个 Agent 分工协作 | "多智能体协作系统" |
| LLM | 大语言模型，如 GPT、Claude | "大语言模型" |
| Prompt | 给 AI 的指令 | "提示词" |
| State | Agent 之间共享的上下文数据 | "状态" |
| Node | 流程图里的一个处理步骤 | "节点" |
| Tool | Agent 能调用的外部功能（搜索、计算） | "工具" |
| RAG | 先检索知识库再让 AI 回答（防幻觉） | "检索增强生成" |
| 容错 | 出错不崩溃，重试或降级 | "鲁棒性设计" |
| API | 程序之间通信的接口 | "接口" |

---

## 最后的话

学习这个项目，记住一条主线：

```
用户输入主题
  → Supervisor 拆任务（规划）
  → Search 搜资料（工具调用）
  → Analyst 做分析（推理）
  → Writer 写报告（生成）
  → 共享白板传递数据（State）
  → LangGraph 控制流转（状态机）
```

**把这条主线讲清楚，你的面试就成功了 80%。** 剩下的 20% 是"你踩过什么坑、怎么解决的"——这需要你真的动手改代码去体会。

加油 💪
