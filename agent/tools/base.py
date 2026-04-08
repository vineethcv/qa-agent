from __future__ import annotations

from abc import ABC, abstractmethod

from agent.state import AgentState


class AgentTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, state: AgentState, **kwargs) -> AgentState:
        raise NotImplementedError