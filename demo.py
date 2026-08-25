# demo.py
"""
一键演示脚本
无需配置 API Key，使用模拟数据演示核心流程
适合：零基础学习、项目展示、环境验证
"""

import os

# 尝试加载 dotenv，如果失败则跳过（demo 模式下不需要真实 API）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 检查是否有真实 API Key
HAS_API_KEY = bool(os.getenv("OPENAI_API_KEY", "").startswith("sk-"))


def run_mock_demo():
    """模拟演示：不依赖真实 API"""
    
    print("=" * 60)
    print("🔬 Multi-Agent Research Assistant — 模拟演示")
    print("=" * 60)
    
    topic = "AI 对教育行业的影响"
    
    print(f"\n📌 研究主题：{topic}\n")
    print("-" * 60)
    
    # Phase 1: Supervisor
    print("\n📋 [Supervisor] 正在分解任务...")
    print("  ✅ 生成 3 个子任务:")
    print("     1. Search（搜索）：搜索 AI+教育 最新资讯")
    print("     2. Analyst（分析）：深度分析关键发现")
    print("     3. Writer（撰写）：生成结构化报告")
    
    # Phase 2: Search Agent
    print("\n🔍 [Search Agent] 正在搜索...")
    import time
    time.sleep(0.5)
    search_results = """
## 搜索结果摘要

1. **[AI在教育领域的应用现状（2024）](https://example.com)**
   全球已有 60% 的教育机构开始尝试 AI 工具，主要应用场景包括：个性化学习路径规划、智能批改、课后辅导等。

2. **[生成式 AI 如何改变课堂教学](https://example.com)**
   OpenAI、Google 等巨头纷纷推出教育专用 AI 产品，ChatGPT Education 版本月活突破 5000 万。

3. **[AI 教育工具的效果评估研究](https://example.com)**
   数据显示，使用 AI 辅助学习的学生平均成绩提升 12%，学习效率提升 30%。
"""
    print(search_results)
    
    # Phase 3: Analyst Agent
    print("\n📊 [Analyst Agent] 正在分析...")
    time.sleep(0.5)
    analysis = """
## 深度分析

### 核心发现
1. **渗透率高**：全球 60% 教育机构已引入 AI，普及速度超预期
2. **效果显著**：AI 辅助学习可提升成绩 12%、效率 30%，有数据支撑
3. **巨头布局**：OpenAI、Google、Microsoft 均推出教育专用产品

### 关键数据
- AI 教育产品月活：5000 万+
- 成绩提升：+12%
- 学习效率提升：+30%

### 一致性与争议
- 一致：各方均认可 AI 在个性化学习方面的价值
- 争议：AI 是否会削弱学生独立思考能力

### 深层洞察
AI 教育正处于「早期采用者」向「早期大众」的跨越阶段，
核心驱动力是「降本增效 + 个性化」，而非「替代教师」。
"""
    print(analysis)
    
    # Phase 4: Writer Agent
    print("\n✍️  [Writer Agent] 正在生成报告...")
    time.sleep(0.5)
    report = """
# 研究报告：AI 对教育行业的影响

## 摘要
AI 正快速渗透教育行业，通过个性化学习和智能工具提升教学效果，但教师角色不可替代。

## 一、背景介绍
随着大语言模型的突破，生成式 AI 在 2023-2024 年迎来爆发式发展。教育行业作为最大的知识传播场景，成为 AI 落地的重要方向之一。

## 二、核心发现

| 应用场景 | 代表产品 | 效果 |
|---------|---------|------|
| 个性化学习 | Khan Academy AI、Socratic | 成绩提升 12% |
| 智能批改 | Gradescope、AI Writing | 效率提升 40% |
| 课后辅导 | ChatGPT、Khanmigo | 24/7 即时响应 |

## 三、深度分析

### 3.1 市场格局
- **巨头主导**：OpenAI（ChatGPT Edu）、Google（Gemini for Education）、Microsoft（Copilot）
- **创业公司**：Khan Academy、Duolingo、Coursera 纷纷接入 AI 能力

### 3.2 效果与挑战
**效果**：有研究表明 AI 辅助学习可提升效率 30%，尤其在数学和编程科目效果显著。

**挑战**：
- 学术诚信问题（AI 代写）
- 教师适应成本
- 数据隐私风险

## 四、趋势与展望

1. **AI Tutor 普及**：一对一 AI 辅导将覆盖更多学生
2. **教师角色升级**：从「知识传授」转向「学习引导」
3. **评估方式变革**：过程性评价取代期末考试

## 五、参考资料
- 基于网络搜索整理，数据截至 2024 年
"""
    print(report)
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
下一步：
1. 配置真实 API Key（OPENAI_API_KEY）
2. 运行完整版本：python -m app.main --topic "你的研究主题"
3. 查看项目 README.md 了解更多
""")


def run_real_demo():
    """真实运行演示：需要 OPENAI_API_KEY"""
    from app.main import run_research
    
    topic = "AI 对教育行业的影响"
    print(f"\n🚀 开始真实研究：{topic}\n")
    
    result = run_research(topic, stream=True)
    
    print("\n" + "=" * 60)
    print("📄 最终报告")
    print("=" * 60)
    print(result.get("report", "（无报告）"))


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 强制使用模拟演示（不需要安装任何依赖，直接看效果）
    # 如需真实运行，请先：pip install -r requirements.txt
    run_mock_demo()
