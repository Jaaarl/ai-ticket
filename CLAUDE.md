# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Platform: Windows (PowerShell)

## Project Overview

Support ticket triage system using LangGraph to route incoming tickets to appropriate teams. Located in `support-triage/`.

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
- `TriageState` (Pydantic model): ticket_id, subject, body, customer_id, plus analysis results
- Enums: `Intent` (BILLING/TECHNICAL/ACCOUNT/FEATURE_REQUEST/UNKNOWN), `Priority` (P0-P3), `Team` (BILLING_TEAM/TECHNICAL_TEAM/ACCOUNT_TEAM)

**Nodes** (`agent/nodes.py`): Each node is a pure function `(TriageState) → TriageState`:
- `analyze_ticket`: Extract urgency signals
- `classify_intent`: Classify ticket type (currently stubbed)
- `route_ticket`: Assign team/priority using intent_map
- `enrich_ticket`: Add KB links and similar tickets
- `process_ticket`: Write decision to ticket system

**LLM Integration** (`agent/llm.py`): Uses MiniMax's Anthropic-compatible API (`MiniMax-M2.7` model) via Anthropic SDK with base URL `https://api.minimax.io/anthropic`.

**Tools** (`agent/tools.py`): LangChain `@tool` decorators for `get_customer`, `update_ticket`, `search_knowledge_base`, `notify_slack` — all stubbed and need real API integration.

## Key Patterns

- Nodes return `state.model_copy(update={...})` to create new state
- Graph built via `StateGraph(TriageState).compile()`
- Parallel execution via `Send` API (shown in integration doc but not yet implemented in graph.py)
- Confidence threshold < 0.7 triggers escalation

## Implementation Status

Nodes are scaffolded with TODOs — LLM calls and real tool integrations need to be added. The graph currently passes state through unchanged.