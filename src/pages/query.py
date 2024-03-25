import streamlit as st
from main import process_desciption
from streamlit_main_page import load_css

load_css()

st.title("Make a query")

search_input = st.text_input("Enter your search query:")

session_state = st.session_state
if "output" not in session_state:
    session_state.output = None


if st.button("Process"):
    (techno, relevant_solutions) = process_desciption(search_input)
    session_state.output = techno

if session_state.output is not None:
    st.write("Output:", session_state.output)