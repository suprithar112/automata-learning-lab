
from graphviz import Digraph


def draw_transition_diagram(
    states,
    alphabet,
    transitions,
    start_state,
    final_states,
    is_nfa=False
):
    graph = Digraph(
        name="TransitionDiagram",
        format="svg"
    )

    graph.attr(
        rankdir="LR",
        bgcolor="white",
        pad="0.3",
        nodesep="0.7",
        ranksep="1.0"
    )

    graph.attr(
        "node",
        shape="circle",
        style="filled",
        fillcolor="white",
        color="#2563eb",
        fontname="Arial",
        fontsize="12"
    )

    graph.attr(
        "edge",
        color="#475569",
        fontname="Arial",
        fontsize="11",
        arrowsize="0.8"
    )

    # Invisible starting point and incoming arrow
    graph.node("START", label="", shape="none")
    graph.edge("START", start_state)

    # Draw states
    for state in states:
        if state in final_states:
            graph.node(
                state,
                shape="doublecircle",
                fillcolor="#dcfce7",
                color="#15803d"
            )
        else:
            graph.node(state)

    # Group transition labels for identical source/destination pairs
    grouped_edges = {}

    for (source, symbol), destinations in transitions.items():

        if is_nfa:
            destinations = sorted(destinations)
        else:
            destinations = [destinations]

        for destination in destinations:
            key = (source, destination)
            grouped_edges.setdefault(key, []).append(symbol)

    for (source, destination), symbols in grouped_edges.items():
        graph.edge(
            source,
            destination,
            label=", ".join(sorted(symbols))
        )

    return graph