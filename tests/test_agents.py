# tests/test_agents.py
"""单元测试"""

import pytest
from unittest.mock import MagicMock, patch


class TestSupervisorAgent:
    """Supervisor Agent 测试"""

    def test_supervisor_initialization(self):
        """测试 Supervisor 初始化"""
        from app.agents.supervisor import create_supervisor_agent
        
        llm = create_supervisor_agent("gpt-4o-mini")
        assert llm is not None
        assert llm.model_name == "gpt-4o-mini"

    def test_research_state_schema(self):
        """测试状态机 schema"""
        from app.agents.supervisor import ResearchState
        
        state: ResearchState = {
            "topic": "测试主题",
            "sub_tasks": [],
            "search_results": "",
            "analysis": "",
            "report": "",
            "current_step": "search",
            "retry_count": {},
            "errors": {},
        }
        
        assert state["topic"] == "测试主题"
        assert state["current_step"] == "search"


class TestSearchAgent:
    """Search Agent 测试"""

    def test_search_agent_creation(self):
        """测试 Search Agent 创建"""
        from app.agents.search_agent import create_search_agent
        
        agent = create_search_agent("gpt-4o-mini")
        assert agent is not None

    @patch("duckduckgo_search.DDGS")
    def test_duckduckgo_search_mock(self, mock_ddgs):
        """测试 DuckDuckGo 搜索（mock）"""
        from app.agents.search_agent import _duckduckgo_search
        
        # Mock 返回值
        mock_instance = MagicMock()
        mock_instance.text.return_value = iter([
            {"title": "Test", "href": "https://test.com", "body": "Test body"}
        ])
        mock_ddgs.return_value.__enter__.return_value = mock_instance
        
        result = _duckduckgo_search("test query")
        
        assert "Test" in result
        assert "test.com" in result


class TestAnalystAgent:
    """Analyst Agent 测试"""

    def test_analyst_agent_creation(self):
        """测试 Analyst Agent 创建"""
        from app.agents.analyst_agent import create_analyst_agent
        
        agent = create_analyst_agent("gpt-4o-mini")
        assert agent is not None


class TestWriterAgent:
    """Writer Agent 测试"""

    def test_writer_agent_creation(self):
        """测试 Writer Agent 创建"""
        from app.agents.writer_agent import create_writer_agent
        
        agent = create_writer_agent("gpt-4o-mini")
        assert agent is not None


class TestRouter:
    """路由测试"""

    def test_should_continue(self):
        """测试路由决策"""
        from app.agents.supervisor import should_continue
        
        assert should_continue({"current_step": "search"}) == "search"
        assert should_continue({"current_step": "analyst"}) == "analyst"
        assert should_continue({"current_step": "writer"}) == "writer"
        assert should_continue({"current_step": "done"}) == "done"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
