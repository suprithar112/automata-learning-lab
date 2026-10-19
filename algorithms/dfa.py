
class DFA:

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
        for (state, symbol), next_state in self.transitions.items():

            if state not in self.states:
                raise ValueError(
                    f"Unknown source state: {state}"
                )

            if symbol not in self.alphabet:
                raise ValueError(
                    f"Invalid alphabet symbol: {symbol}"
                )

            if next_state not in self.states:
                raise ValueError(
                    f"Unknown destination state: {next_state}"
                )

    def validate(self):
        """
        Check that every state has a transition
        for every symbol in the alphabet.
        """

        for state in self.states:
            for symbol in self.alphabet:

                if (state, symbol) not in self.transitions:
                    raise ValueError(
                        f"Missing transition for ({state}, {symbol})"
                    )

        return True

    def process_string(self, input_string):
        """
        Process the input from the start state.
        Accept if the final state is an accepting state.
        """

        current_state = self.start_state

        trace = [
            ("START", current_state)
        ]

        for symbol in input_string:

            if symbol not in self.alphabet:
                return {
                    "accepted": False,
                    "trace": trace,
                    "error": f"Invalid input symbol: {symbol}"
                }

            transition_key = (current_state, symbol)

            if transition_key not in self.transitions:
                return {
                    "accepted": False,
                    "trace": trace,
                    "error": (
                        f"Missing transition for "
                        f"({current_state}, {symbol})"
                    )
                }

            current_state = self.transitions[transition_key]

            trace.append(
                (symbol, current_state)
            )

        return {
            "accepted": current_state in self.final_states,
            "trace": trace,
            "final_state": current_state
        }