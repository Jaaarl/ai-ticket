from pydantic import BaseModel
from enum import Enum

class Intent(Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    UNKNOWN = "unknown"

class Priority(Enum):
    P0 = "p0"  # Critical
    P1 = "p1"  # High
    P2 = "p2"  # Medium
    P3 = "p3"  # Low

class Team(Enum):
    BILLING_TEAM = "billing_team"
    TECHNICAL_TEAM = "technical_team"
    ACCOUNT_TEAM = "account_team"

class TriageState(BaseModel):
    ticket_id: str
    subject: str
    body: str
    customer_id: str
    customer_tier: str = "free"
    
    intent: Intent = None
    priority: Priority = None
    team: Team = None
    confidence: float = 0.0
    
    needs_escalation: bool = False
    kb_links: list[str] = []
    similar_ticket_ids: list[str] = []
