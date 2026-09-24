from app.llm_client import llm_client

SYSTEM_PROMPT = """You are a helpful customer support agent for TravelZone, \
a travel booking platform. Answer the user's question using ONLY the \
context provided below. Be concise and friendly. If the context does not \
fully answer the question, say what you can and suggest the user ask for \
a human agent.

Context:
{context}
"""


class SupportAgent:
    """Generates a grounded answer from retrieved knowledge-base context."""

    def run(self, query: str, context: str) -> str:
        system_prompt = SYSTEM_PROMPT.format(context=context)
        return llm_client.generate(system_prompt, query)


support_agent = SupportAgent()
