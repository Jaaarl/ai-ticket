from langchain_core.tools import tool
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def get_customer(customer_id: str) -> dict:
    """Fetch customer details."""
    return {"tier": "free", "name": "Customer"}

@tool
def update_ticket(ticket_id: str, team: str, priority: str, intent: str):
    """Write routing decision back to ticket system."""
    print(f"[update_ticket] {ticket_id} -> team={team}, priority={priority}, intent={intent}")

@tool
def search_knowledge_base(query: str) -> list[dict]:
    """Search KB for related articles."""
    # TODO: Replace with your actual KB API (Confluence, Notion, internal docs, etc.)
    # Returns stub KB links for demo purposes
    return [
        {"title": "API Error Troubleshooting", "url": "https://kb.example.com/api-errors"},
        {"title": "500 Internal Server Error Guide", "url": "https://kb.example.com/500-errors"},
    ]

@tool
def notify_discord(message: str) -> dict:
    """Send escalation notification to Discord via webhook."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print(f"[notify_discord] DISCORD_WEBHOOK_URL not set, skipping: {message}")
        return {"ok": False, "error": "no webhook URL"}
    response = httpx.post(webhook_url, json={"content": message}, timeout=10)
    return {"ok": response.status_code == 200}
