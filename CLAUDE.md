# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Platform: Windows (PowerShell)
Python 3.11+
Dependencies: `langgraph`, `langchain-core`, `anthropic`, `pydantic`, `httpx`, `python-dotenv`

## Setup

```bash
# Add your API keys to .env
cp support-triage/.env support-triage/.env  # edit support-triage/.env directly
```

## Commands

```bash
# Run the triage pipeline
python support-triage/test/run_test.py
```

## Architecture

**State Graph** (`agent/graph.py`): Linear 5-node pipeline:
```
analyze → classify → route → enrich → process → END
```

**State Schema** (`agent/state.py`):
- `TriageState` (Pydantic model): ticket_id, subject, body, customer_id, customer_tier, plus routing results
- Enums: `Intent` (BILLING/TECHNICAL/ACCOUNT/FEATURE_REQUEST/UNKNOWN), `Priority` (P0-P3), `Team` (BILLING_TEAM/TECHNICAL_TEAM/ACCOUNT_TEAM)

**Nodes** (`agent/nodes.py`): Each node is a pure function `(TriageState) → TriageState`:
- `analyze_ticket`: Fetches customer tier, detects urgency keywords (outage, down, critical, etc.)
- `classify_intent`: Calls LLM via `classify_with_ai()`, maps response to `Intent` enum via keyword matching
- `route_ticket`: Assigns team and priority from `intent_map`
- `enrich_ticket`: Searches KB via `search_knowledge_base`, populates `kb_links`
- `process_ticket`: Calls `update_ticket` and `notify_discord` (if escalation needed)

**LLM Integration** (`agent/llm.py`): MiniMax's Anthropic-compatible API (`MiniMax-M2.7` model) via Anthropic SDK with base URL `https://api.minimax.io/anthropic`. Uses `load_dotenv()` to load `.env`.

**Tools** (`agent/tools.py`): LangChain `@tool` decorators:
- `get_customer`: Returns stub customer data (replace with real CRM API)
- `update_ticket`: Prints routing decision (replace with real ticketing system API)
- `search_knowledge_base`: Returns stub KB articles (replace with real KB API)
- `notify_discord`: Posts escalation to Discord webhook via `DISCORD_WEBHOOK_URL` env var

## Key Patterns

- Nodes return `state.model_copy(update={...})` to create new state
- Graph built via `StateGraph(TriageState).compile()`
- Escalation fires when `needs_escalation` is `True` (set by low LLM confidence <0.7 OR urgency keywords detected)
- Discord webhook URL set via `DISCORD_WEBHOOK_URL` in `.env` — gracefully skips if not set
