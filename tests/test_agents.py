from app.agents.escalation_agent import escalation_agent
from app.agents.orchestrator import orchestrator
from app.agents.retrieval_agent import retrieval_agent
from app.tools import check_order_status, create_support_ticket


def test_retrieval_agent_confident_on_known_topic():
    result = retrieval_agent.run("How do I reset my password?")
    assert result.confident
    assert result.sources


def test_retrieval_agent_not_confident_on_unrelated_topic():
    result = retrieval_agent.run("What is the airspeed velocity of an unladen swallow?")
    assert not result.confident


def test_escalation_agent_returns_an_action():
    result = escalation_agent.run("My flight got cancelled and I need a refund urgently")
    assert result["action"] in ("create_support_ticket", "check_order_status", "text")


def test_orchestrator_routes_known_topic_to_support():
    response = orchestrator.handle("Can I change my travel dates?")
    assert response.route == "support"
    assert response.reply


def test_orchestrator_routes_unknown_topic_to_escalation():
    response = orchestrator.handle("Purple elephants juggle unrelated topics near Neptune")
    assert response.route == "escalation"
    assert response.reply


def test_create_support_ticket_tool():
    ticket = create_support_ticket(subject="Test issue", priority="high")
    assert ticket["ticket_id"].startswith("TCK-")
    assert ticket["priority"] == "high"


def test_check_order_status_tool_found():
    result = check_order_status("a1001")
    assert result["found"] is True
    assert result["status"] == "Shipped"


def test_check_order_status_tool_not_found():
    result = check_order_status("Z9999")
    assert result["found"] is False
