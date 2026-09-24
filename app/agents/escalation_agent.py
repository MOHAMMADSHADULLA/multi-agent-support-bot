from app.llm_client import llm_client
from app.tools import TOOL_DEFINITIONS, TOOL_IMPLEMENTATIONS

SYSTEM_PROMPT = """You are the escalation handler for TravelZone customer \
support. The knowledge base could not confidently answer the user's \
question. Decide whether to:
  1. Call `check_order_status` if the user is asking about an existing order/booking.
  2. Call `create_support_ticket` for anything else that needs a human to follow up.
Always take one of these two actions - do not just apologize."""


class EscalationAgent:
    """Handles queries the Retrieval/Support agents couldn't resolve, by
    invoking a tool (ticket creation or order lookup) instead of free-text
    generation. This is the piece of the pipeline that demonstrates real
    function/tool calling rather than plain chat completion."""

    def run(self, query: str) -> dict:
        decision = llm_client.generate_with_tools(SYSTEM_PROMPT, query, TOOL_DEFINITIONS)

        if decision["type"] == "tool_call":
            tool_name = decision["name"]
            args = decision.get("arguments", {})
            impl = TOOL_IMPLEMENTATIONS.get(tool_name)
            if impl is None:
                return {"action": "error", "detail": f"Unknown tool '{tool_name}'"}
            result = impl(**args)
            return {"action": tool_name, "arguments": args, "result": result}

        return {"action": "text", "result": decision["content"]}


escalation_agent = EscalationAgent()
