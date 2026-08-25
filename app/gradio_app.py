# app/gradio_app.py
"""
Gradio Web UI
本地快速体验，无需启动 API 服务
"""

import gradio as gr
from .main import run_research

# 全局模型选项（可根据你 .env 配置的提供商修改）
MODELS = [
    "qwen-plus",        # 阿里云千问（当前使用）
    "deepseek-chat",    # DeepSeek
    "glm-4-flash",      # 智谱（免费）
]


def research_with_ui(topic: str, model: str, progress=gr.Progress()):
    """
    Gradio UI 的回调函数
    使用 progress 回调显示执行进度
    """
    if not topic or len(topic.strip()) < 2:
        return "❌ 请输入有效的研究主题（至少2个字）", ""
    
    topic = topic.strip()
    
    progress(0.1, desc="📋 Supervisor 规划任务中...")
    
    result = run_research(topic, model_name=model, stream=False)
    
    progress(0.3, desc="🔍 Search Agent 搜索中...")
    search_results = result.get("search_results", "")
    
    progress(0.6, desc="📊 Analyst Agent 分析中...")
    analysis = result.get("analysis", "")
    
    progress(0.9, desc="✍️ Writer Agent 生成报告中...")
    report = result.get("report", "")
    
    progress(1.0, desc="✅ 完成！")
    
    # 拼接中间过程
    intermediate = f"""## 🔍 搜索结果
{search_results or '（无）'}

---

## 📊 分析洞察
{analysis or '（无）'}
"""
    
    return intermediate, report


# ---------------------------------------------------------------------------
# Gradio 界面定义
# ---------------------------------------------------------------------------

block = gr.Blocks(
    title="Multi-Agent Research Assistant",
)

with block:
    gr.Markdown("""
    # 🔬 Multi-Agent Research Assistant
    ### 基于 LangGraph 的多智能体研究助手
    
    ---
    
    输入一个研究主题，Supervisor 会自动调度 Search / Analyst / Writer 三个 Agent 协作完成研究。
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            topic_input = gr.Textbox(
                label="📌 研究主题",
                placeholder="例如：AI 对教育行业的影响",
                lines=2,
            )
        
        with gr.Column(scale=1):
            model_select = gr.Dropdown(
                label="🤖 模型",
                choices=MODELS,
                value=MODELS[0],
            )
    
    submit_btn = gr.Button("🚀 开始研究", variant="primary")
    
    with gr.Tabs():
        with gr.TabItem("📊 中间过程"):
            intermediate_output = gr.Markdown(value="*提交后将显示各 Agent 的执行结果*")
        
        with gr.TabItem("📄 最终报告"):
            final_output = gr.Markdown(value="*研究报告将显示在这里*")
    
    gr.Markdown("""
    ---
    
    ### 💡 使用说明
    
    1. 输入研究主题（越具体效果越好）
    2. 选择模型（默认 gpt-4o-mini，性价比最高）
    3. 点击「开始研究」等待完成
    4. 查看「中间过程」了解 Agent 协作详情
    5. 查看「最终报告」获取完整研究结果
    
    ### 🏗️ 技术架构
    
    ```
    Supervisor Agent（任务规划）
         ↓
    ┌────┴────┐
    ↓         ↓
    Search   Analyst
    ↓         ↓
    └────┬────┘
         ↓
      Writer（生成报告）
    ```
    """)

    # 绑定事件
    submit_btn.click(
        fn=research_with_ui,
        inputs=[topic_input, model_select],
        outputs=[intermediate_output, final_output],
    )


if __name__ == "__main__":
    block.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Soft(),
    )
