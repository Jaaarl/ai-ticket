import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import triage_graph
from agent.state import TriageState

state = TriageState(
    ticket_id="TICK-001",
    subject="API returns 500 error",
    body="Getting Internal Server Error on /payments endpoint",
    customer_id="CUST-123"
)

result = triage_graph.invoke(state)

print(f"Ticket: {result.get('ticket_id')}")
print(f"Customer Tier: {result.get('customer_tier')}")
print(f"Intent: {result.get('intent')}")
print(f"Team: {result.get('team')}")
print(f"Priority: {result.get('priority')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Needs Escalation: {result.get('needs_escalation')}")
