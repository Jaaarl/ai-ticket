from langgraph.graph import StateGraph, END
from .state import TriageState
from .nodes import analyze_ticket, classify_intent, route_ticket, enrich_ticket, process_ticket


def build_triage_graph():
    graph = StateGraph(TriageState)

    graph.add_node("analyze", analyze_ticket)
    graph.add_node("classify", classify_intent)
    graph.add_node("route", route_ticket)
    graph.add_node("enrich", enrich_ticket)
    graph.add_node("process", process_ticket)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "classify")
    graph.add_edge("classify", "route")
    graph.add_edge("route", "enrich")
    graph.add_edge("enrich", "process")
    graph.add_edge("process", END)

    return graph.compile()

triage_graph = build_triage_graph()
