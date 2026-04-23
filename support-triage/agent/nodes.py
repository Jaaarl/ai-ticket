from .state import TriageState, Intent, Priority, Team

def analyze_ticket(state: TriageState) -> TriageState:
    """Extract urgency signals and customer context."""
    # TODO: Call LLM or use keyword extraction
    return state

def classify_intent(state: TriageState) -> TriageState:
    """Classify as billing/technical/account/feature."""
    # TODO: Call LLM for classification
    return state

def route_ticket(state: TriageState) -> TriageState:
    """Assign team and priority."""
    # Map intent → team
    intent_map = {
        Intent.BILLING: Team.BILLING_TEAM,
        Intent.TECHNICAL: Team.TECHNICAL_TEAM,
        Intent.ACCOUNT: Team.ACCOUNT_TEAM,
    }
    return state

def enrich_ticket(state: TriageState) -> TriageState:
    """Add KB links and similar tickets."""
    return state

def process_ticket(state: TriageState) -> TriageState:
    """Write final decision to your system."""
    return state
