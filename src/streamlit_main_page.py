import streamlit as st
from utils.design import load_css, nav_bar
from utils.database import DatabaseObject, SolutionDB

st.set_page_config(layout="wide")
session_state = st.session_state
if "current_page" not in session_state:
    session_state.current_page = "page_main"

if "solutions" not in session_state:
    DatabaseObject.cursor.execute(
        f"""SELECT numsolution FROM tblsolution""")
    solution_ids = [x[0] for x in DatabaseObject.cursor.fetchall()]
    solutions = [SolutionDB(id) for id in solution_ids]
    st.session_state["solutions"] = solutions
# Load custom CSS styles
load_css()
nav_bar(st.session_state["solutions"])
