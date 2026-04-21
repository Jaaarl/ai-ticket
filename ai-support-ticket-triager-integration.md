# AI Support Ticket Triager - Integration Guide

Integrating LangGraph workflows into an existing support ticket system.

---

## Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐
│   Ticket    │───▶│   Webhook/   │───▶│   LangGraph         │
│   Created   │    │   API        │    │   Workflow          │
└─────────────┘    └──────────────┘    └─────────────────────┘
                                                  │
                       ┌──────────────────────────┼──────────────────────────┐
                       ▼                          ▼                          ▼
              ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
              │   Analyze    │          │   Route      │          │   Enrich     │
              │   Ticket     │─────────▶│   Ticket     │─────────▶│   Ticket     │
              └──────────────┘          └──────────────┘          └──────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │  Update Ticket   │
                                              │  in DB           │
                                              └──────────────────┘
```

---

## LangGraph Workflow Design

### Node Definitions

| Node | Responsibility |
|------|---------------|
| `analyze_ticket` | Extract subject, urgency signals, customer tier |
| `classify_intent` | Categorize as Billing, Technical, Account, or Feature Request |
| `route_ticket` | Determine team, priority, and escalation flags |
| `enrich_ticket` | Add knowledge base links, similar tickets, SLA info |
| `update_ticket` | Write routing decision back to your database |

### Conditional Routing Rules

```
confidence < 0.7    ──▶  escalate_to_human()
priority == P1      ──▶  notify_oncall_slack()
intent == billing   ──▶  route_to_premium_queue()  [if enterprise tier]
```

---

## Integration Points

| Your System | LangGraph Integration |
|-------------|----------------------|
| Ticket Created Event | Webhook triggers `graph.run(ticket_id)` |
| Team/Queue Database | Tools for reading/writing routing decisions |
| Customer Data | Tool to fetch customer tier, history |
| Knowledge Base | Tool to search KB for related articles |
| Slack/Email | Tool to send notifications |
| Feedback Mechanism | Human corrections stored as training data |

---

## Features to Add

### 1. Auto-Triage
Automatically route incoming tickets to the correct team based on intent classification.

### 2. Priority Detection
Flag P0/P1 tickets for immediate attention and page on-call staff.

### 3. Escalation Detection
Identify ambiguous or high-stakes tickets that require human review.

### 4. Auto-Reply Draft
Generate a suggested first response based on ticket content and knowledge base.

### 5. Link Similar Tickets
Find related open tickets to prevent duplicate work and help agents.

### 6. SLA Risk Scoring
Predict which tickets are at risk of breaching SLA based on queue depth and priority.

---

## Implementation: Auto-Triage Workflow

### Project Structure

```
support-triage/
├── agent/
│   ├── __init__.py
│   ├── state.py          # Typed state + schema
│   ├── nodes.py          # Graph nodes
│   ├── tools.py          # Tool definitions
│   ├── graph.py          # Graph construction
│   └── models.py         # Pydantic models
├── api/
│   └── webhooks.py       # FastAPI webhook endpoint
├── tests/
│   └── test_triage.py
└── pyproject.toml
```

### 1. State Definition

```python
# agent/state.py
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class Intent(Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    UNKNOWN = "unknown"

class Priority(Enum):
    P0 = "p0"  # Critical - immediate response
    P1 = "p1"  # High - within 4 hours
    P2 = "p2"  # Medium - within 24 hours
    P3 = "p3"  # Low - within 48 hours

class Team(Enum):
    BILLING_TEAM = "billing_team"
    TECHNICAL_TEAM = "technical_team"
    ACCOUNT_TEAM = "account_team"
    PRODUCT_TEAM = "product_team"
    PREMIUM_QUEUE = "premium_queue"  # Enterprise billing

class TriageState(BaseModel):
    ticket_id: str
    subject: str
    body: str
    customer_id: str
    customer_tier: str = "free"  # free, pro, enterprise

    # Analysis results (populated by nodes)
    intent: Optional[Intent] = None
    priority: Optional[Priority] = None
    team: Optional[Team] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None

    # Flags
    needs_escalation: bool = False
    escalation_reason: Optional[str] = None

    # Enrichment
    kb_links: list[str] = []
    similar_ticket_ids: list[str] = []
    suggested_reply: Optional[str] = None

    # Error handling
    error: Optional[str] = None
```

### 2. Tool Definitions

```python
# agent/tools.py
from langchain_core.tools import tool
from typing import Optional
import httpx

@tool
def get_customer(customer_id: str) -> dict:
    """Fetch customer details from your system."""
    # Replace with your actual API call
    response = httpx.get(f"https://your-api.com/customers/{customer_id}")
    return response.json()

@tool
def get_ticket(ticket_id: str) -> dict:
    """Fetch ticket details from your system."""
    response = httpx.get(f"https://your-api.com/tickets/{ticket_id}")
    return response.json()

@tool
def update_ticket(
    ticket_id: str,
    team: str,
    priority: str,
    intent: str,
    confidence: float,
    kb_links: list[str] = [],
    similar_ticket_ids: list[str] = [],
) -> dict:
    """Update ticket with triage decisions."""
    response = httpx.patch(
        f"https://your-api.com/tickets/{ticket_id}",
        json={
            "team": team,
            "priority": priority,
            "intent": intent,
            "triage_confidence": confidence,
            "kb_links": kb_links,
            "similar_ticket_ids": similar_ticket_ids,
            "triage_status": "completed",
        }
    )
    return response.json()

@tool
def search_knowledge_base(query: str) -> list[dict]:
    """Search internal knowledge base for related articles."""
    response = httpx.post(
        "https://your-api.com/kb/search",
        json={"query": query, "limit": 3}
    )
    return response.json().get("articles", [])

@tool
def find_similar_tickets(subject: str, ticket_id: str) -> list[str]:
    """Find open tickets with similar subjects."""
    response = httpx.post(
        "https://your-api.com/tickets/similar",
        json={"subject": subject, "exclude_id": ticket_id, "status": "open"}
    )
    return response.json().get("ticket_ids", [])

@tool
def notify_slack(channel: str, message: str) -> dict:
    """Send notification to Slack channel."""
    response = httpx.post(
        "https://slack-webhook-url.com",
        json={"channel": channel, "text": message}
    )
    return response.json()

@tool
def create_feedback_log(
    ticket_id: str,
    predicted_intent: str,
    corrected_intent: Optional[str] = None,
    corrected_team: Optional[str] = None,
) -> dict:
    """Log human corrections for model improvement."""
    response = httpx.post(
        "https://your-api.com/feedback",
        json={
            "ticket_id": ticket_id,
            "predicted_intent": predicted_intent,
            "corrected_intent": corrected_intent,
            "corrected_team": corrected_team,
            "feedback_source": "triage_review",
        }
    )
    return response.json()
```

### 3. Graph Nodes

```python
# agent/nodes.py
from .state import TriageState, Intent, Priority, Team
from .tools import (
    get_customer,
    search_knowledge_base,
    find_similar_tickets,
    update_ticket,
    notify_slack,
)
import httpx

def analyze_ticket(state: TriageState) -> TriageState:
    """
    Node 1: Analyze ticket content and customer context.
    Extracts urgency signals and enriched customer info.
    """
    # Fetch customer data
    customer = get_customer.invoke({"customer_id": state.customer_id})

    # Build analysis prompt
    prompt = f"""
    Analyze this support ticket:

    Subject: {state.subject}
    Body: {state.body}
    Customer Tier: {customer.get('tier', 'unknown')}

    Identify:
    1. Urgency signals (keywords like 'urgent', 'broken', 'down', 'ASAP')
    2. Customer sentiment (frustrated, angry, neutral, patient)
    3. Any SLA-relevant context

    Return a JSON with: urgency_score (0-1), sentiment, key_phrases[]
    """

    # Call LLM (replace with your actual LLM call)
    # response = llm.invoke(prompt)
    response = {"urgency_score": 0.5, "sentiment": "neutral", "key_phrases": []}

    # Update state with analysis
    return {
        **state.model_dump(),
        "customer_tier": customer.get("tier", "free"),
    }

def classify_intent(state: TriageState) -> TriageState:
    """
    Node 2: Classify ticket intent using LLM.
    """
    prompt = f"""
    Classify this ticket into ONE of these categories:
    - billing: Payment, subscription, invoice, refund issues
    - technical: Bugs, errors, integration issues, API problems
    - account: Login issues, password reset, profile updates, permissions
    - feature_request: New features, improvements, suggestions

    Subject: {state.subject}
    Body: {state.body}

    Return JSON with: intent, confidence (0-1), reasoning
    """

    # response = llm.invoke(prompt)
    response = {
        "intent": "technical",
        "confidence": 0.85,
        "reasoning": "Keywords indicate API integration issue"
    }

    return {
        **state.model_dump(),
        "intent": Intent(response["intent"]),
        "confidence": response["confidence"],
        "reasoning": response["reasoning"],
    }

def route_ticket(state: TriageState) -> TriageState:
    """
    Node 3: Route ticket to appropriate team with priority.
    """
    # Map intent -> default team
    intent_team_map = {
        Intent.BILLING: Team.BILLING_TEAM,
        Intent.TECHNICAL: Team.TECHNICAL_TEAM,
        Intent.ACCOUNT: Team.ACCOUNT_TEAM,
        Intent.FEATURE_REQUEST: Team.PRODUCT_TEAM,
        Intent.UNKNOWN: Team.TECHNICAL_TEAM,
    }

    team = intent_team_map.get(state.intent, Team.TECHNICAL_TEAM)

    # Enterprise billing goes to premium queue
    if state.intent == Intent.BILLING and state.customer_tier == "enterprise":
        team = Team.PREMIUM_QUEUE

    # Determine priority based on urgency signals
    priority = Priority.P3
    if any(kw in state.subject.lower() for kw in ["down", "outage", "critical", "broken"]):
        priority = Priority.P0
    elif state.customer_tier == "enterprise":
        priority = Priority.P2

    # Check for escalation needed
    needs_escalation = state.confidence < 0.7
    escalation_reason = None
    if state.confidence < 0.7:
        escalation_reason = f"Low confidence ({state.confidence:.0%}) - human review needed"

    return {
        **state.model_dump(),
        "team": team,
        "priority": priority,
        "needs_escalation": needs_escalation,
        "escalation_reason": escalation_reason,
    }

def enrich_ticket(state: TriageState) -> TriageState:
    """
    Node 4: Add knowledge base links and similar tickets.
    """
    kb_articles = search_knowledge_base.invoke({
        "query": f"{state.subject} {state.body[:200]}"
    })

    similar_tickets = find_similar_tickets.invoke({
        "subject": state.subject,
        "ticket_id": state.ticket_id,
    })

    return {
        **state.model_dump(),
        "kb_links": [a["url"] for a in kb_articles],
        "similar_ticket_ids": similar_tickets,
    }

def process_ticket(state: TriageState) -> TriageState:
    """
    Node 5: Write final decision to ticket system.
    """
    if state.needs_escalation:
        # Log for human review queue
        pass

    update_ticket.invoke({
        "ticket_id": state.ticket_id,
        "team": state.team.value,
        "priority": state.priority.value,
        "intent": state.intent.value,
        "confidence": state.confidence,
        "kb_links": state.kb_links,
        "similar_ticket_ids": state.similar_ticket_ids,
    })

    return state

def handle_escalation(state: TriageState) -> TriageState:
    """
    Node: Handle tickets that need human review.
    """
    notify_slack.invoke({
        "channel": "#triage-escalations",
        "message": f"Escalated ticket {state.ticket_id}: {state.escalation_reason}"
    })
    return state
```

### 4. Graph Construction

```python
# agent/graph.py
from langgraph.graph import StateGraph, END
from .state import TriageState
from .nodes import (
    analyze_ticket,
    classify_intent,
    route_ticket,
    enrich_ticket,
    process_ticket,
    handle_escalation,
)

def should_escalate(state: TriageState) -> str:
    """Conditional edge: check if escalation needed."""
    if state.needs_escalation:
        return "escalate"
    return "continue"

def build_triage_graph():
    """
    Build the triage StateGraph.

    Flow:
        analyze -> classify -> route -> [escalate?] -> enrich -> update
    """
    graph = StateGraph(TriageState)

    # Add nodes
    graph.add_node("analyze", analyze_ticket)
    graph.add_node("classify", classify_intent)
    graph.add_node("route", route_ticket)
    graph.add_node("enrich", enrich_ticket)
    graph.add_node("process", process_ticket)
    graph.add_node("escalate", handle_escalation)

    # Set entry point
    graph.set_entry_point("analyze")

    # Linear flow: analyze -> classify -> route
    graph.add_edge("analyze", "classify")
    graph.add_edge("classify", "route")

    # Conditional branch from route
    graph.add_conditional_edges(
        "route",
        should_escalate,
        {
            "escalate": "escalate",
            "continue": "enrich",
        }
    )

    # Continue to enrich after escalation (or skip if not needed)
    graph.add_edge("escalate", "enrich")

    # Final step
    graph.add_edge("enrich", "process")
    graph.add_edge("process", END)

    return graph.compile()


# Singleton instance
triage_graph = build_triage_graph()
```

### 5. API Webhook

```python
# api/webhooks.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import triage_graph
from agent.state import TriageState
import httpx

app = FastAPI()

class TicketWebhook(BaseModel):
    ticket_id: str
    subject: str
    body: str
    customer_id: str
    event_type: str = "ticket.created"

@app.post("/webhooks/ticket")
async def handle_ticket_webhook(webhook: TicketWebhook):
    """Receive ticket created events and run triage."""
    if webhook.event_type != "ticket.created":
        return {"status": "ignored", "reason": "unsupported event"}

    try:
        # Initialize state
        initial_state = TriageState(
            ticket_id=webhook.ticket_id,
            subject=webhook.subject,
            body=webhook.body,
            customer_id=webhook.customer_id,
        )

        # Run the graph
        result = await triage_graph.ainvoke(initial_state)

        return {
            "status": "success",
            "ticket_id": webhook.ticket_id,
            "routed_to": result.team.value,
            "priority": result.priority.value,
            "confidence": result.confidence,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 6. Usage Example

```python
# examples/run_triage.py
from agent.graph import triage_graph
from agent.state import TriageState

# Sync usage
state = TriageState(
    ticket_id="TICK-1234",
    subject="API returns 500 on payment endpoint",
    body="Getting Internal Server Error when calling /payments API...",
    customer_id="CUST-5678",
)

result = triage_graph.invoke(state)

print(f"Routed to: {result.team.value}")
print(f"Priority: {result.priority.value}")
print(f"Confidence: {result.confidence:.0%}")
print(f"KB Links: {result.kb_links}")
```

### 7. Testing

```python
# tests/test_triage.py
import pytest
from agent.graph import triage_graph
from agent.state import TriageState, Intent, Priority, Team

def test_billing_ticket_routes_to_billing():
    state = TriageState(
        ticket_id="TICK-001",
        subject="Invoice question",
        body="Can I get an invoice for last month?",
        customer_id="CUST-001",
    )

    result = triage_graph.invoke(state)

    assert result.intent == Intent.BILLING
    assert result.team == Team.BILLING_TEAM

def test_enterprise_billing_routes_to_premium():
    state = TriageState(
        ticket_id="TICK-002",
        subject="Refund request",
        body="I need a refund for...",
        customer_id="CUST-002",
        customer_tier="enterprise",
    )

    result = triage_graph.invoke(state)

    assert result.intent == Intent.BILLING
    assert result.team == Team.PREMIUM_QUEUE

def test_low_confidence_triggers_escalation():
    state = TriageState(
        ticket_id="TICK-003",
        subject="Something is wrong",
        body="Not working...",
        customer_id="CUST-003",
    )

    result = triage_graph.invoke(state)

    assert result.needs_escalation == True
    assert result.confidence < 0.7
```

---

## Feedback Loop

```
Agent reviews ticket → Makes correction → Correction stored to feedback DB
                                                      │
                                                      ▼
                                           Retrain/update routing model
```

Human corrections improve future routing accuracy over time.

---

## Next Steps

1. Identify your ticket data schema
2. Map existing team/queue structure
3. Choose first feature to implement (suggest: Auto-Triage)
4. Build integration API/webhook
5. Add feedback loop for continuous improvement
