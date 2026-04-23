from langchain_core.tools import tool
import httpx

@tool
def get_customer(customer_id: str) -> dict:
    """Fetch customer details."""
    # Replace with your actual API
    return {"tier": "free", "name": "Customer"}

@tool
def update_ticket(ticket_id: str, team: str, priority: str, intent: str):
    """Write routing decision back to ticket system."""
    # Replace with your actual API call
    pass

@tool
def search_knowledge_base(query: str) -> list[dict]:
    """Search KB for related articles."""
    return []

@tool
def notify_slack(channel: str, message: str) -> dict:
    """Send Slack notification."""
    pass
