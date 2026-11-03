"""AI subpackage for CustomerInsight AI.

High‑level assistant utilities live here. The module re‑exports the
functions from the original ``ai_assistant`` file so existing imports
continue to work.
"""

from __future__ import annotations

from ..ai_assistant import ask_assistant, AssistantResponse, TOOL_REGISTRY

__all__ = ["ask_assistant", "AssistantResponse", "TOOL_REGISTRY"]

