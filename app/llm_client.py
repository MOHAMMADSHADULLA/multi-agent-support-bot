"""
Thin, swappable wrapper around whichever LLM provider is configured.

The rest of the codebase only calls `generate()` and `generate_with_tools()`
- it never imports openai or google-generativeai directly. That keeps the
agents provider-agnostic and makes it trivial to add a third provider later.
"""
from __future__ import annotations

import json
from typing import Any

from app.config import settings


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider

    # ------------------------------------------------------------------ #
    # Plain text generation (used by the Support agent)
    # ------------------------------------------------------------------ #
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "openai":
            return self._openai_generate(system_prompt, user_prompt)
        if self.provider == "gemini":
            return self._gemini_generate(system_prompt, user_prompt)
        return self._mock_generate(system_prompt, user_prompt)

    # ------------------------------------------------------------------ #
    # Tool-calling generation (used by the Escalation agent)
    # Returns either {"type": "text", "content": str}
    #             or {"type": "tool_call", "name": str, "arguments": dict}
    # ------------------------------------------------------------------ #
    def generate_with_tools(
        self, system_prompt: str, user_prompt: str, tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if self.provider == "openai":
            return self._openai_tools(system_prompt, user_prompt, tools)
        if self.provider == "gemini":
            return self._gemini_tools(system_prompt, user_prompt, tools)
        return self._mock_tools(system_prompt, user_prompt, tools)

    # ------------------------------------------------------------------ #
    # OpenAI
    # ------------------------------------------------------------------ #
    def _openai_client(self):
        from openai import OpenAI  # lazy import so the mock/gemini paths don't need the package

        return OpenAI(api_key=settings.openai_api_key)

    def _openai_generate(self, system_prompt: str, user_prompt: str) -> str:
        client = self._openai_client()
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""

    def _openai_tools(self, system_prompt, user_prompt, tools):
        client = self._openai_client()
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
            for t in tools
        ]
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tools=openai_tools,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            call = msg.tool_calls[0]
            return {
                "type": "tool_call",
                "name": call.function.name,
                "arguments": json.loads(call.function.arguments or "{}"),
            }
        return {"type": "text", "content": msg.content or ""}

    # ------------------------------------------------------------------ #
    # Gemini
    # ------------------------------------------------------------------ #
    def _gemini_generate(self, system_prompt: str, user_prompt: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            settings.gemini_model, system_instruction=system_prompt
        )
        resp = model.generate_content(user_prompt)
        return resp.text or ""

    def _gemini_tools(self, system_prompt, user_prompt, tools):
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        gemini_tools = [
            {
                "function_declarations": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    }
                    for t in tools
                ]
            }
        ]
        model = genai.GenerativeModel(
            settings.gemini_model,
            system_instruction=system_prompt,
            tools=gemini_tools,
        )
        resp = model.generate_content(user_prompt)
        parts = resp.candidates[0].content.parts
        for part in parts:
            fc = getattr(part, "function_call", None)
            if fc and fc.name:
                return {"type": "tool_call", "name": fc.name, "arguments": dict(fc.args)}
        return {"type": "text", "content": resp.text or ""}

    # ------------------------------------------------------------------ #
    # Mock provider - deterministic, no network calls. Used by default and
    # in CI so the whole pipeline (retrieval -> orchestration -> tool call)
    # is exercised without needing a paid API key.
    # ------------------------------------------------------------------ #
    def _mock_generate(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "[mock-llm] Based on the retrieved knowledge base context, here is "
            "an answer to: " + user_prompt[:200]
        )

    def _mock_tools(self, system_prompt, user_prompt, tools):
        import re

        lowered = user_prompt.lower()
        order_match = re.search(r"\b([A-Za-z]\d{4})\b", user_prompt)
        wants_order_lookup = order_match or "order" in lowered
        if wants_order_lookup and any(t["name"] == "check_order_status" for t in tools):
            return {
                "type": "tool_call",
                "name": "check_order_status",
                "arguments": {"order_id": order_match.group(1) if order_match else "UNKNOWN"},
            }
        if any(t["name"] == "create_support_ticket" for t in tools):
            return {
                "type": "tool_call",
                "name": "create_support_ticket",
                "arguments": {
                    "subject": user_prompt[:60],
                    "priority": "normal",
                },
            }
        return {"type": "text", "content": self._mock_generate(system_prompt, user_prompt)}


llm_client = LLMClient()
