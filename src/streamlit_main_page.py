import streamlit as st
from utils.design import load_css, nav_bar

session_state = st.session_state
if "current_page" not in session_state:
    session_state.current_page = "page_main"

# Load custom CSS styles
load_css()

nav_bar()
