import streamlit as st
from utils.run_part1 import process_description
from utils.design import load_css, nav_bar

load_css()
nav_bar()

st.title("Make a query")

search_input = st.text_input("Enter your search query:")

session_state = st.session_state
if "output" not in session_state:
    session_state.output = None


if st.button("Process"):
    (techno, relevant_solutions) = process_description(search_input)
    session_state.output = techno

if session_state.output is not None:
    st.write("Output:", session_state.output)
