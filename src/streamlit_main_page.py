import streamlit as st
from utils.design import load_all_page_requirements
from utils.database import DatabaseObject, SolutionDB

st.set_page_config(layout="wide")
session_state = st.session_state
if "current_page" not in session_state:
    session_state.current_page = "page_main"


load_all_page_requirements()
