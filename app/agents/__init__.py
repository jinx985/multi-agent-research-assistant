# app/agents/__init__.py
"""Agent module — exports all agent factories."""

from .supervisor import create_supervisor_agent
from .search_agent import create_search_agent
from .analyst_agent import create_analyst_agent
from .writer_agent import create_writer_agent

__all__ = [
    "create_supervisor_agent",
    "create_search_agent",
    "create_analyst_agent",
    "create_writer_agent",
]
