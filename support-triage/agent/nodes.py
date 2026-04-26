from .state import TriageState, Intent, Priority, Team
from .llm import classify_with_ai
from .tools import get_customer, update_ticket, notify_discord

def analyze_ticket(state: TriageState) -> TriageState:
    """Extract urgency signals and customer context."""
    # Fetch customer tier
    customer = get_customer.invoke({"customer_id": state.customer_id})
    customer_tier = customer.get("tier", "free")

    # Extract urgency signals from subject + body
    text = (state.subject + " " + state.body).lower()
    urgency_keywords = ["outage", "down", "critical", "production", "urgent", "emergency", "p0", "p1"]
    is_urgent = any(kw in text for kw in urgency_keywords)

    return state.model_copy(update={
        "customer_tier": customer_tier,
        "needs_escalation": is_urgent or state.needs_escalation,
    })

def classify_intent(state: TriageState) -> TriageState:
    """Classify as billing/technical/account/feature."""
    result = classify_with_ai(state.subject, state.body)
    intent_str = result["intent"].strip().lower()
    confidence = result.get("confidence", 0.0)

    # Map LLM output to Intent enum - check for keywords in the response
    intent_lower = intent_str.lower()
    if "billing" in intent_lower or "invoice" in intent_lower or "payment" in intent_lower and "500" not in intent_lower:
        intent = Intent.BILLING
    elif "technical" in intent_lower or "bug" in intent_lower or "500" in intent_lower or "error" in intent_lower:
        intent = Intent.TECHNICAL
    elif "account" in intent_lower or "login" in intent_lower or "password" in intent_lower:
        intent = Intent.ACCOUNT
    elif "feature" in intent_lower or "request" in intent_lower:
        intent = Intent.FEATURE_REQUEST
    else:
        intent = Intent.UNKNOWN

    needs_escalation = (confidence < 0.7) or state.needs_escalation

    return state.model_copy(update={
        "intent": intent,
        "confidence": confidence,
        "needs_escalation": needs_escalation,
    })

def route_ticket(state: TriageState) -> TriageState:
    """Assign team and priority."""
    intent_map = {
        Intent.BILLING: (Team.BILLING_TEAM, Priority.P1),
        Intent.TECHNICAL: (Team.TECHNICAL_TEAM, Priority.P2),
        Intent.ACCOUNT: (Team.ACCOUNT_TEAM, Priority.P2),
        Intent.FEATURE_REQUEST: (Team.TECHNICAL_TEAM, Priority.P3),
    }
    team, priority = Team.TECHNICAL_TEAM, Priority.P2  # default fallback
    if state.intent in intent_map:
        team, priority = intent_map[state.intent]
    return state.model_copy(update={"team": team, "priority": priority})

def enrich_ticket(state: TriageState) -> TriageState:
    """Add KB links and similar tickets."""
    return state

def process_ticket(state: TriageState) -> TriageState:
    """Write final decision to your system."""
    update_ticket.invoke({
        "ticket_id": state.ticket_id,
        "team": state.team.value if state.team else "unassigned",
        "priority": state.priority.value if state.priority else "p3",
        "intent": state.intent.value if state.intent else "unknown",
    })
    if state.needs_escalation:
        notify_discord.invoke({
            "channel": "#triage-escalations",
            "message": f"[ESCALATION] Ticket {state.ticket_id} ({state.priority.value if state.priority else '?'}) assigned to {state.team.value if state.team else '?'}",
        })
    return state
