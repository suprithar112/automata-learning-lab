
import streamlit as st
import re

from algorithms.dfa import DFA
from algorithms.nfa import NFA
from algorithms.nfa_to_dfa import convert_nfa_to_dfa
from visualization.transition_diagram import draw_transition_diagram

from algorithms.dfa_minimization import minimize_dfa


st.set_page_config(
    page_title="Automata Learning Lab",
    page_icon="🔤",
    layout="wide"
)

st.title("🔤 Automata Learning Lab")
st.write(
    "Create finite automata, visualize transition diagrams, "
    "test strings, and convert NFAs into equivalent DFAs."
)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Choose a module",
    [
        "Home",
        "DFA Simulator",
        "NFA Simulator",
        "NFA to DFA Conversion",
        "DFA Minimization",
        "Regular Expression Tester"
    ]
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def parse_list(value):
    """Convert comma-separated input into a list."""
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def validate_common_inputs(
    states,
    alphabet,
    start_state,
    final_states
):
    """Validate states, alphabet, start state and final states."""

    if not states:
        raise ValueError("Enter at least one state.")

    if not alphabet:
        raise ValueError("Enter at least one alphabet symbol.")

    if len(set(states)) != len(states):
        raise ValueError("State names must be unique.")

    if len(set(alphabet)) != len(alphabet):
        raise ValueError("Alphabet symbols must be unique.")

    if any("," in state or "|" in state for state in states):
        raise ValueError(
            "State names cannot contain commas or |."
        )

    if any("," in symbol or "|" in symbol for symbol in alphabet):
        raise ValueError(
            "Alphabet symbols cannot contain commas or |."
        )

    if any(len(symbol) != 1 for symbol in alphabet):
        raise ValueError(
            "Each alphabet symbol must be one character, "
            "for example: 0,1."
        )

    if not start_state:
        raise ValueError("Enter a start state.")

    if start_state not in states:
        raise ValueError(
            "The start state must be included in the states list."
        )

    if not set(final_states).issubset(set(states)):
        raise ValueError(
            "All accepting states must be included in the states list."
        )


def parse_dfa_transitions(text):
    """
    DFA format:
    source,symbol,destination

    Example:
    A,0,A
    A,1,B
    """

    transitions = {}

    for line_number, line in enumerate(
        text.splitlines(), start=1
    ):
        line = line.strip()

        if not line:
            continue

        parts = [part.strip() for part in line.split(",")]

        if len(parts) != 3 or not all(parts):
            raise ValueError(
                f"Line {line_number}: use source,symbol,destination."
            )

        source, symbol, destination = parts
        key = (source, symbol)

        if key in transitions:
            raise ValueError(
                f"Line {line_number}: duplicate transition "
                f"for {source} with {symbol}."
            )

        transitions[key] = destination

    return transitions


def parse_nfa_transitions(text):
    """
    NFA format:
    source,symbol,destination1|destination2

    Use - when there is no destination.
    """

    transitions = {}

    for line_number, line in enumerate(
        text.splitlines(), start=1
    ):
        line = line.strip()

        if not line:
            continue

        parts = [part.strip() for part in line.split(",")]

        if len(parts) != 3 or not all(parts):
            raise ValueError(
                f"Line {line_number}: use "
                "source,symbol,destinations."
            )

        source, symbol, destination_text = parts
        key = (source, symbol)

        if key in transitions:
            raise ValueError(
                f"Line {line_number}: duplicate transition "
                f"for {source} with {symbol}."
            )

        if destination_text == "-":
            destinations = set()
        else:
            destination_list = [
                item.strip()
                for item in destination_text.split("|")
            ]

            if any(not item for item in destination_list):
                raise ValueError(
                    f"Line {line_number}: destination names "
                    "cannot be empty. Use - for no destination."
                )

            destinations = set(destination_list)

        transitions[key] = destinations

    return transitions


def show_result(result, automaton_type):
    """Display whether a string is accepted and show its trace."""

    if "error" in result:
        st.error(result["error"])
        return

    if result["accepted"]:
        st.success(
            "ACCEPTED: The input string belongs to the language."
        )
    else:
        st.error(
            "REJECTED: The input string does not belong "
            "to the language."
        )

    st.subheader("Step-by-Step Execution")

    for step, (symbol, current) in enumerate(result["trace"]):
        if step == 0:
            st.write(f"Step 0 — Start: {current}")
        else:
            st.write(
                f"Step {step} — Read '{symbol}': {current}"
            )

    if automaton_type == "DFA":
        st.write("Final state:", result["final_state"])
    else:
        st.write(
            "States after input:",
            result["final_states_reached"]
        )


def show_automaton_details(
    states,
    alphabet,
    transitions,
    start_state,
    final_states,
    is_nfa
):
    """Display a transition table and diagram."""

    st.subheader("Automaton Details")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**States:**", sorted(states))
        st.write("**Alphabet:**", sorted(alphabet))

    with col2:
        st.write("**Start state:**", start_state)
        st.write("**Accepting states:**", sorted(final_states))

    st.subheader("Transition Table")

    rows = []

    for (source, symbol), destination in transitions.items():
        if is_nfa:
            destination_text = (
                ", ".join(sorted(destination))
                if destination
                else "∅"
            )
            rows.append({
                "Current state": source,
                "Input symbol": symbol,
                "Next states": destination_text
            })
        else:
            rows.append({
                "Current state": source,
                "Input symbol": symbol,
                "Next state": destination
            })

    st.dataframe(rows, use_container_width=True)

    st.subheader("Transition Diagram")
    st.caption(
        "The incoming arrow identifies the start state. "
        "Double circles represent accepting states."
    )

    diagram = draw_transition_diagram(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state=start_state,
        final_states=final_states,
        is_nfa=is_nfa
    )

    st.graphviz_chart(
        diagram,
        use_container_width=True
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if page == "Home":
    st.header("Welcome to Automata Learning Lab")

    st.write(
        """
        This project demonstrates important concepts from
        Theory of Computation.

        **Available modules:**

        - DFA Simulator — build and test deterministic finite automata.
        - NFA Simulator — build and test nondeterministic finite automata.
        - NFA to DFA Conversion — use subset construction.
        - DFA Minimization — reserved for a future implementation.
        - Regular Expression Tester — reserved for a future implementation.
        """
    )

    st.info(
        "Select a module from the sidebar to get started."
    )


# --------------------------------------------------
# DFA AND NFA SIMULATORS
# --------------------------------------------------

elif page in ["DFA Simulator", "NFA Simulator"]:

    is_dfa = page == "DFA Simulator"
    automaton_type = "DFA" if is_dfa else "NFA"

    st.header(f"{automaton_type} Simulator")

    st.write(
        "Define your automaton, visualize its transitions, "
        "and test an input string."
    )

    with st.form(f"{automaton_type.lower()}_definition"):

        states_text = st.text_input(
            "States (comma-separated)",
            value="A,B"
        )

        alphabet_text = st.text_input(
            "Input alphabet (comma-separated)",
            value="0,1"
        )

        start_state_text = st.text_input(
            "Start state",
            value="A"
        )

        final_states_text = st.text_input(
            "Accepting states (comma-separated)",
            value="B"
        )

        if is_dfa:
            default_transitions = (
                "A,0,A\n"
                "A,1,B\n"
                "B,0,A\n"
                "B,1,B"
            )

            help_text = (
                "One transition per line: source,symbol,destination"
            )
        else:
            default_transitions = (
                "A,0,A\n"
                "A,1,A|B\n"
                "B,0,-\n"
                "B,1,-"
            )

            help_text = (
                "One transition per line: source,symbol,destinations. "
                "Use | between multiple destinations and - for none."
            )

        transitions_text = st.text_area(
            "Transition rules",
            value=default_transitions,
            help=help_text,
            height=150
        )

        input_string = st.text_input(
            "Input string to test",
            value="101"
        )

        submitted = st.form_submit_button("Build and Run")

    if submitted:
        try:
            states = parse_list(states_text)
            alphabet = parse_list(alphabet_text)
            final_states = parse_list(final_states_text)
            start_state = start_state_text.strip()

            validate_common_inputs(
                states,
                alphabet,
                start_state,
                final_states
            )

            if is_dfa:
                transitions = parse_dfa_transitions(
                    transitions_text
                )

                automaton = DFA(
                    states=states,
                    alphabet=alphabet,
                    transitions=transitions,
                    start_state=start_state,
                    final_states=final_states
                )

                # A DFA must define a transition for every
                # state and every alphabet symbol.
                automaton.validate()

            else:
                transitions = parse_nfa_transitions(
                    transitions_text
                )

                automaton = NFA(
                    states=states,
                    alphabet=alphabet,
                    transitions=transitions,
                    start_state=start_state,
                    final_states=final_states
                )

            show_automaton_details(
                states=states,
                alphabet=alphabet,
                transitions=transitions,
                start_state=start_state,
                final_states=final_states,
                is_nfa=not is_dfa
            )

            st.subheader("String Simulation")

            result = automaton.process_string(input_string)
            show_result(result, automaton_type)

        except (ValueError, TypeError) as error:
            st.error(f"Input or automaton error: {error}")

        except Exception as error:
            st.error(f"An unexpected error occurred: {error}")


# --------------------------------------------------
# NFA TO DFA CONVERSION
# --------------------------------------------------

elif page == "NFA to DFA Conversion":

    st.header("NFA to DFA Conversion")

    st.write(
        """
        Convert an NFA into an equivalent DFA using the
        **Subset Construction Algorithm**.

        Enter an NFA below. Each transition can lead to multiple
        states, separated by `|`.
        """
    )

    with st.form("nfa_to_dfa_form"):

        states_text = st.text_input(
            "NFA states (comma-separated)",
            value="A,B"
        )

        alphabet_text = st.text_input(
            "Input alphabet (comma-separated)",
            value="0,1"
        )

        start_state_text = st.text_input(
            "NFA start state",
            value="A"
        )

        final_states_text = st.text_input(
            "NFA accepting states (comma-separated)",
            value="B"
        )

        nfa_transitions_text = st.text_area(
            "NFA transition rules",
            value=(
                "A,0,A\n"
                "A,1,A|B\n"
                "B,0,-\n"
                "B,1,-"
            ),
            height=150,
            help=(
                "Format: source,symbol,destinations. "
                "Example: A,1,A|B. Use - for no destination."
            )
        )

        convert_button = st.form_submit_button(
            "Convert NFA to DFA"
        )

    if convert_button:
        try:
            nfa_states = parse_list(states_text)
            nfa_alphabet = parse_list(alphabet_text)
            nfa_start_state = start_state_text.strip()
            nfa_final_states = parse_list(final_states_text)

            validate_common_inputs(
                nfa_states,
                nfa_alphabet,
                nfa_start_state,
                nfa_final_states
            )

            nfa_transitions = parse_nfa_transitions(
                nfa_transitions_text
            )

            # Build the NFA from the user's inputs.
            nfa = NFA(
                states=nfa_states,
                alphabet=nfa_alphabet,
                transitions=nfa_transitions,
                start_state=nfa_start_state,
                final_states=nfa_final_states
            )

            # Convert the NFA into an equivalent DFA.
            converted_dfa = convert_nfa_to_dfa(nfa)

            # Check that the converted DFA is complete.
            converted_dfa.validate()

            st.success("NFA converted successfully!")

            st.subheader("Original NFA")

            show_automaton_details(
                states=nfa_states,
                alphabet=nfa_alphabet,
                transitions=nfa_transitions,
                start_state=nfa_start_state,
                final_states=nfa_final_states,
                is_nfa=True
            )

            st.subheader("Converted DFA")

            st.write(
                "**DFA states:**",
                sorted(converted_dfa.states)
            )

            st.write(
                "**Input alphabet:**",
                sorted(converted_dfa.alphabet)
            )

            st.write(
                "**DFA start state:**",
                converted_dfa.start_state
            )

            st.write(
                "**DFA accepting states:**",
                sorted(converted_dfa.final_states)
            )

            st.caption(
                "A DFA state represents a subset of NFA states. "
                "EMPTY represents the empty subset, if reached."
            )

            show_automaton_details(
                states=converted_dfa.states,
                alphabet=converted_dfa.alphabet,
                transitions=converted_dfa.transitions,
                start_state=converted_dfa.start_state,
                final_states=converted_dfa.final_states,
                is_nfa=False
            )

            st.subheader("Test the Converted DFA")

            test_string = st.text_input(
                "Enter a string to test",
                value="101",
                key="converted_dfa_test_string"
            )

            if st.button("Run Converted DFA"):
                result = converted_dfa.process_string(test_string)
                show_result(result, "DFA")

        except (ValueError, TypeError) as error:
            st.error(f"Conversion input error: {error}")

        except Exception as error:
            st.error(f"Conversion failed: {error}")


# --------------------------------------------------
# DFA MINIMIZATION
# --------------------------------------------------



elif page == "DFA Minimization":
    st.header("⚙️ DFA Minimization")
    st.write(
        "Enter a DFA, minimize it, and compare the original "
        "and minimized automata."
    )

    # Input form
    with st.form("minimize_dfa_form"):
        states_text = st.text_input(
            "States (comma-separated)",
            value="A, B, C, D"
        )

        alphabet_text = st.text_input(
            "Alphabet (comma-separated)",
            value="0, 1"
        )

        start_state_text = st.text_input(
            "Start state",
            value="A"
        )

        final_states_text = st.text_input(
            "Final states (comma-separated)",
            value="C"
        )

        transitions_text = st.text_area(
            "Transitions (source,symbol,destination)",
            value=(
                "A,0,B\n"
                "A,1,C\n"
                "B,0,B\n"
                "B,1,C\n"
                "C,0,D\n"
                "C,1,C\n"
                "D,0,B\n"
                "D,1,C"
            ),
            height=180
        )

        submitted = st.form_submit_button("Minimize DFA")

    if submitted:
        try:
            # Read and validate inputs
            states = parse_list(states_text)
            alphabet = parse_list(alphabet_text)
            final_states = parse_list(final_states_text)
            start_state = start_state_text.strip()

            validate_common_inputs(
                states,
                alphabet,
                start_state,
                final_states
            )

            transitions = parse_dfa_transitions(transitions_text)

            # Build original DFA
            original_dfa = DFA(
                states=states,
                alphabet=alphabet,
                transitions=transitions,
                start_state=start_state,
                final_states=final_states
            )

            original_dfa.validate()

            # Minimize DFA
            minimized_dfa = minimize_dfa(original_dfa)

            # Store results between Streamlit reruns
            st.session_state["original_min_dfa"] = original_dfa
            st.session_state["result_min_dfa"] = minimized_dfa

            st.success("DFA minimized successfully!")

        except Exception as error:
            st.error(f"Error: {error}")

    # Display results
    original_dfa = st.session_state.get("original_min_dfa")
    minimized_dfa = st.session_state.get("result_min_dfa")

    if original_dfa is not None and minimized_dfa is not None:
        st.subheader("📊 State Count Comparison")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Original States",
            len(original_dfa.states)
        )

        col2.metric(
            "Minimized States",
            len(minimized_dfa.states)
        )

        col3.metric(
            "States Removed",
            len(original_dfa.states) - len(minimized_dfa.states)
        )

        col1, col2 = st.columns(2)

        # Original DFA
        with col1:
            st.subheader("Original DFA")

            show_automaton_details(
                states=original_dfa.states,
                alphabet=original_dfa.alphabet,
                transitions=original_dfa.transitions,
                start_state=original_dfa.start_state,
                final_states=original_dfa.final_states,
                is_nfa=False
            )

        # Minimized DFA
        with col2:
            st.subheader("Minimized DFA")

            show_automaton_details(
                states=minimized_dfa.states,
                alphabet=minimized_dfa.alphabet,
                transitions=minimized_dfa.transitions,
                start_state=minimized_dfa.start_state,
                final_states=minimized_dfa.final_states,
                is_nfa=False
            )

        # Test strings against both automata
        st.divider()
        st.subheader("🧪 Test an Input String")

        with st.form("min_dfa_test_form"):
            test_string = st.text_input(
                "Enter an input string",
                value="0101"
            )

            test_clicked = st.form_submit_button("Compare DFA Results")

        if test_clicked:
            try:
                original_result = original_dfa.process_string(test_string)
                minimized_result = minimized_dfa.process_string(test_string)

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Original DFA Result**")
                    show_result(original_result, "DFA")

                with col2:
                    st.write("**Minimized DFA Result**")
                    show_result(minimized_result, "DFA")

                if (
                    original_result["accepted"]
                    == minimized_result["accepted"]
                ):
                    st.success(
                        "Both DFAs agree on this input string."
                    )
                else:
                    st.error(
                        "The results differ. Check the minimization algorithm."
                    )

            except Exception as error:
                st.error(f"Could not test the string: {error}")

    
# --------------------------------------------------
# REGULAR EXPRESSION TESTER
# --------------------------------------------------

elif page == "Regular Expression Tester":

    st.header("🔎 Regular Expression Tester")

    st.write(
        "Enter a regular expression and an input string "
        "to check whether the entire string matches the pattern."
    )

    st.info(
        "This tester uses Python's regular expression syntax. "
        "It supports common patterns used to study regular expressions."
    )

    with st.form("regex_tester_form"):

        regex_pattern = st.text_input(
            "Regular Expression",
            value="a(b|c)*",
            help="Example: a(b|c)*"
        )

        input_string = st.text_input(
            "Input String",
            value="abcb",
            help="Enter the string you want to test."
        )

        submitted = st.form_submit_button("Test Regular Expression")

    if submitted:
        try:
            # Compile the user's regular expression.
            compiled_pattern = re.compile(regex_pattern)

            # Check whether the entire string matches.
            match = compiled_pattern.fullmatch(input_string)

            st.subheader("Test Result")

            if match:
                st.success(
                    "MATCH: The entire input string matches "
                    "the regular expression."
                )
            else:
                st.error(
                    "NO MATCH: The input string does not match "
                    "the regular expression."
                )

            st.write("**Regular Expression:**", regex_pattern)
            st.write("**Input String:**", repr(input_string))

        except re.error as error:
            st.error(f"Invalid regular expression: {error}")

    st.divider()

    st.subheader("📘 Regular Expression Examples")

    st.markdown("""
    | Regular Expression | Meaning | Example that matches |
    |---|---|---|
    | `a` | Exactly the character `a` | `a` |
    | `a*` | Zero or more `a` characters | `aaa` |
    | `a+` | One or more `a` characters | `aaa` |
    | `a(b|c)` | `a` followed by `b` or `c` | `ab` |
    | `(0|1)*` | Any string of binary digits, including the empty string | `1010` |
    | `a(b|c)*` | `a` followed by zero or more `b` or `c` characters | `abcb` |
    """)

    st.caption(
        "Note: Python regular expressions support additional features "
        "beyond the basic regular expressions studied in automata theory."
    )
