
class NFA:

    def __init__(
        self,
        states,
        alphabet,
        transitions,
        start_state,
        final_states
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = set(final_states)

        # Validate basic configuration
        if not self.states:
            raise ValueError("States cannot be empty.")

        if not self.alphabet:
            raise ValueError("Alphabet cannot be empty.")

        if start_state not in self.states:
            raise ValueError(
                "Start state must belong to states."
            )

        if not self.final_states.issubset(self.states):
            raise ValueError(
                "Final states must belong to states."
            )

        # Validate transitions
        for (state, symbol), destinations in self.transitions.items():

            if state not in self.states:
                raise ValueError(
                    f"Unknown source state: {state}"
                )

            if symbol not in self.alphabet:
                raise ValueError(
                    f"Invalid alphabet symbol: {symbol}"
                )

            if not set(destinations).issubset(self.states):
                raise ValueError(
                    "Transition contains an unknown destination state."
                )

    def process_string(self, input_string):
        """
        Track every possible current state.
        Accept if at least one path ends in a final state.
        """

        current_states = {self.start_state}

        trace = [
            ("START", sorted(current_states))
        ]

        for symbol in input_string:

            if symbol not in self.alphabet:
                return {
                    "accepted": False,
                    "trace": trace,
                    "error": f"Invalid input symbol: {symbol}"
                }

            next_states = set()

            for state in current_states:

                destinations = self.transitions.get(
                    (state, symbol),
                    set()
                )

                next_states.update(destinations)

            current_states = next_states

            trace.append(
                (symbol, sorted(current_states))
            )

        accepted = bool(
            current_states & self.final_states
        )

        return {
            "accepted": accepted,
            "trace": trace,
            "final_states_reached": sorted(current_states)
        }