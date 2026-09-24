import re
from dataclasses import dataclass, field

from app.agents.escalation_agent import escalation_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.support_agent import support_agent

# Matches order IDs like "A1001". The knowledge base has no content about
# specific orders, so TF-IDF similarity on these queries is noisy - a query
# containing an order ID is routed straight to the Escalation agent's
# order-lookup tool rather than trusting RAG confidence.
_ORDER_ID_PATTERN = re.compile(r"\b[A-Za-z]\d{4}\b")


@dataclass
class ChatResponse:
    reply: str
    route: str  # "support" | "escalation"
    sources: list[str] = field(default_factory=list)
    tool_result: dict | None = None


class Orchestrator:
    """Entry point for a single user message. Runs retrieval first; if the
    retrieved context is strong enough, the Support agent answers from it.
    Otherwise the query is handed off to the Escalation agent, which decides
    between filing a ticket or looking up an order via tool calls."""

    def handle(self, message: str) -> ChatResponse:
        looks_like_order_lookup = bool(_ORDER_ID_PATTERN.search(message))
        retrieval = retrieval_agent.run(message)

        if retrieval.confident and not looks_like_order_lookup:
            reply = support_agent.run(message, retrieval.context)
            return ChatResponse(reply=reply, route="support", sources=retrieval.sources)

        escalation = escalation_agent.run(message)

        if escalation["action"] == "create_support_ticket":
            ticket = escalation["result"]
            reply = (
                f"I couldn't find that in our docs, so I've opened ticket "
                f"{ticket['ticket_id']} (priority: {ticket['priority']}). "
                f"A human agent will follow up shortly."
            )
        elif escalation["action"] == "check_order_status":
            result = escalation["result"]
            if result.get("found"):
                reply = (
                    f"Order {result['order_id']} is currently '{result['status']}', "
                    f"expected by {result['eta']}."
                )
            else:
                reply = (
                    f"I couldn't find an order with ID '{result['order_id']}'. "
                    f"Could you double-check the order ID?"
                )
        else:
            reply = escalation["result"]

        return ChatResponse(
            reply=reply, route="escalation", sources=[], tool_result=escalation
        )


orchestrator = Orchestrator()
