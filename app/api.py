# app/api.py
"""
FastAPI REST API
提供 HTTP 接口，可被前端、移动端或其他服务调用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import asyncio

from .main import run_research

app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="多智能体研究助手 REST 接口",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 请求/响应模型
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str = Field(..., min_length=2, max_length=500, description="研究主题")
    model: Optional[str] = Field("gpt-4o-mini", description="使用的模型")
    stream: Optional[bool] = Field(True, description="是否流式输出")


class ResearchResponse(BaseModel):
    """研究响应"""
    topic: str
    status: str
    report: Optional[str] = None
    search_results: Optional[str] = None
    analysis: Optional[str] = None
    errors: Optional[dict] = None


class HealthResponse(BaseModel):
    """健康检查"""
    status: str
    version: str


# ---------------------------------------------------------------------------
# 接口定义
# ---------------------------------------------------------------------------

@app.get("/", response_model=HealthResponse)
async def root():
    """健康检查"""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    提交研究任务
    
    Request Body:
    ```json
    {
        "topic": "AI 对教育行业的影响",
        "model": "gpt-4o-mini",
        "stream": false
    }
    ```
    
    Response:
    ```json
    {
        "topic": "AI 对教育行业的影响",
        "status": "completed",
        "report": "# 研究报告...",
        "search_results": "...",
        "analysis": "...",
        "errors": {}
    }
    ```
    """
    try:
        # 在独立线程中运行（避免阻塞事件循环）
        result = await asyncio.to_thread(
            run_research,
            topic=request.topic,
            model_name=request.model,
            stream=False,  # API 模式关闭流式
        )
        
        return ResearchResponse(
            topic=result.get("topic", request.topic),
            status="completed" if result.get("report") else "partial",
            report=result.get("report"),
            search_results=result.get("search_results"),
            analysis=result.get("analysis"),
            errors=result.get("errors"),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/{topic}")
async def get_research_status(topic: str, model: Optional[str] = "gpt-4o-mini"):
    """
    快捷研究接口（GET 方法）
    直接在 URL 中传入研究主题
    """
    result = await asyncio.to_thread(
        run_research,
        topic=topic,
        model_name=model,
        stream=False,
    )
    
    return {
        "topic": topic,
        "status": "completed",
        "report": result.get("report", "（无报告）"),
        "word_count": len(result.get("report", "")),
    }
