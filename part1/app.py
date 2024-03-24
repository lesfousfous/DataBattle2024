import streamlit as st

# Example data structure for solutions
solutions = [
    {"title": "Solution 1", "description": "Description of Solution 1"},
    {"title": "Solution 2", "description": "Description of Solution 2"},
    {"title": "Solution 3", "description": "Description of Solution 3"},
]

# Initialize session state
if "show_details" not in st.session_state:
    st.session_state.show_details = False
if "current_solution" not in st.session_state:
    st.session_state.current_solution = {}


def show_solution_details(solution):
    """Callback function to show solution details."""
    st.session_state.current_solution = solution
    st.session_state.show_details = True


# Main page layout
if not st.session_state.show_details:
    st.title("Solutions")
    for solution in solutions:
        link = st.button(solution["title"])
        if link:
            show_solution_details(solution)
else:
    # Details popup-like page
    st.title(st.session_state.current_solution["title"])
    st.write(st.session_state.current_solution["description"])

    if st.button("Back"):
        st.session_state.show_details = False
