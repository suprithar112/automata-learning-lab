
from collections import deque

from algorithms.dfa import DFA


def convert_nfa_to_dfa(nfa):
    """
    Convert an NFA into an equivalent DFA
    using the subset construction algorithm.
    """

    start_subset = frozenset([nfa.start_state])

    queue = deque([start_subset])
    discovered = {start_subset}

    transitions = {}

    while queue:
        current_subset = queue.popleft()

        for symbol in nfa.alphabet:
            next_subset = set()

            for state in current_subset:
                destinations = nfa.transitions.get(
                    (state, symbol),
                    set()
                )
                next_subset.update(destinations)

            next_subset = frozenset(next_subset)

            if next_subset not in discovered:
                discovered.add(next_subset)
                queue.append(next_subset)

            transitions[
                (subset_name(current_subset), symbol)
            ] = subset_name(next_subset)

    states = {
        subset_name(subset)
        for subset in discovered
    }

    start_state = subset_name(start_subset)

    final_states = {
        subset_name(subset)
        for subset in discovered
        if subset & nfa.final_states
    }

    return DFA(
        states=states,
        alphabet=nfa.alphabet,
        transitions=transitions,
        start_state=start_state,
        final_states=final_states
    )


def subset_name(subset):
    """
    Convert a set of NFA states into a readable DFA state name.
    The empty subset is represented by EMPTY.
    """

    if not subset:
        return "EMPTY"

    return "{" + ",".join(sorted(subset)) + "}"