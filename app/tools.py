"""
Mock "actions" the Escalation agent can take when a question can't be
answered from the knowledge base. In a production system these would call
a real ticketing system (Zendesk, Jira Service Desk) or an orders API -
they're stubbed here so the whole pipeline is runnable and testable
without external credentials.
"""
from __future__ import annotations

import itertools
import uuid
from typing import Any

_ticket_counter = itertools.count(1000)

_MOCK_ORDERS = {
    "A1001": {"status": "Shipped", "eta": "2026-09-25"},
    "A1002": {"status": "Processing", "eta": "2026-09-28"},
    "A1003": {"status": "Delivered", "eta": "2026-09-18"},
}

# JSON-schema style definitions, shared with both the OpenAI and Gemini
# tool-calling formats via app/llm_client.py.
TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "create_support_ticket",
        "description": (
            "File a support ticket for a question the knowledge base could not "
            "answer, so a human agent can follow up."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Short summary of the issue"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"],
                },
            },
            "required": ["subject"],
        },
    },
    {
        "name": "check_order_status",
        "description": "Look up the shipping status of a customer order by order ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. A1001"},
            },
            "required": ["order_id"],
        },
    },
]


def create_support_ticket(subject: str, priority: str = "normal") -> dict[str, Any]:
    ticket_id = f"TCK-{next(_ticket_counter)}"
    return {
        "ticket_id": ticket_id,
        "subject": subject,
        "priority": priority,
        "status": "open",
        "tracking_ref": str(uuid.uuid4())[:8],
    }


def check_order_status(order_id: str) -> dict[str, Any]:
    order = _MOCK_ORDERS.get(order_id.upper())
    if not order:
        return {"order_id": order_id, "found": False}
    return {"order_id": order_id.upper(), "found": True, **order}


TOOL_IMPLEMENTATIONS = {
    "create_support_ticket": create_support_ticket,
    "check_order_status": check_order_status,
}
