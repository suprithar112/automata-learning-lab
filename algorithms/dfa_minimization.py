
from algorithms.dfa import DFA


def minimize_dfa(dfa):
    """
    Minimize a complete DFA using partition refinement.

    Steps:
    1. Validate the DFA transitions.
    2. Remove unreachable states.
    3. Partition final and non-final states.
    4. Refine partitions to merge equivalent states.
    5. Build and return the minimized DFA.
    """

    states = set(dfa.states)
    alphabet = set(dfa.alphabet)
    transitions = dfa.transitions
    final_states = set(dfa.final_states)
    start_state = dfa.start_state

    # --------------------------------------------------
    # Step 1: Validate the DFA
    # --------------------------------------------------

    if not states:
        raise ValueError("The DFA must contain at least one state.")

    if start_state not in states:
        raise ValueError("The start state must belong to the states set.")

    if not final_states.issubset(states):
        raise ValueError("All final states must belong to the states set.")

    # --------------------------------------------------
    # Step 2: Find reachable states
    # --------------------------------------------------

    reachable = set()
    stack = [start_state]

    while stack:
        current_state = stack.pop()

        if current_state in reachable:
            continue

        reachable.add(current_state)

        for symbol in alphabet:
            destination = transitions.get((current_state, symbol))

            if destination is None:
                raise ValueError(
                    f"Missing transition from state '{current_state}' "
                    f"for symbol '{symbol}'. "
                    "Please provide a complete DFA."
                )

            if destination not in states:
                raise ValueError(
                    f"Transition from '{current_state}' with symbol "
                    f"'{symbol}' leads to unknown state '{destination}'."
                )

            if destination not in reachable:
                stack.append(destination)

    # Remove unreachable states.
    states = reachable
    final_states = final_states.intersection(states)

    non_final_states = states - final_states

    # --------------------------------------------------
    # Step 3: Create initial partitions
    # --------------------------------------------------

    partitions = []

    if final_states:
        partitions.append(final_states)

    if non_final_states:
        partitions.append(non_final_states)

    # --------------------------------------------------
    # Step 4: Refine partitions
    # --------------------------------------------------

    while True:
        state_to_group = {}

        for index, group in enumerate(partitions):
            for state in group:
                state_to_group[state] = index

        refined_partitions = []

        for group in partitions:
            split_groups = {}

            for state in group:
                # Record the destination group for each symbol.
                signature = tuple(
                    state_to_group[transitions[(state, symbol)]]
                    for symbol in sorted(alphabet)
                )

                if signature not in split_groups:
                    split_groups[signature] = set()

                split_groups[signature].add(state)

            refined_partitions.extend(split_groups.values())

        # If no group was split, refinement is complete.
        if len(refined_partitions) == len(partitions):
            partitions = refined_partitions
            break

        partitions = refined_partitions

    # --------------------------------------------------
    # Step 5: Assign a new name to each partition
    # --------------------------------------------------

    def make_state_name(group):
        return "{" + ",".join(sorted(group)) + "}"

    state_names = {}

    for group in partitions:
        new_name = make_state_name(group)

        for old_state in group:
            state_names[old_state] = new_name

    minimized_states = set(state_names.values())
    minimized_start_state = state_names[start_state]

    minimized_final_states = {
        state_names[state] for state in final_states
    }

    # --------------------------------------------------
    # Step 6: Build transitions for the minimized DFA
    # --------------------------------------------------

    minimized_transitions = {}

    for group in partitions:
        representative = next(iter(group))
        new_source = state_names[representative]

        for symbol in alphabet:
            old_destination = transitions[(representative, symbol)]
            new_destination = state_names[old_destination]

            minimized_transitions[(new_source, symbol)] = new_destination

    # --------------------------------------------------
    # Step 7: Return the minimized DFA
    # --------------------------------------------------

    return DFA(
        states=minimized_states,
        alphabet=alphabet,
        transitions=minimized_transitions,
        start_state=minimized_start_state,
        final_states=minimized_final_states
    )
