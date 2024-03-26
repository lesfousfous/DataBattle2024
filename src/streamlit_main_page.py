import streamlit as st

st.set_page_config(layout="wide")
session_state = st.session_state
if "current_page" not in session_state:
    session_state.current_page = "page_main"


def load_css():
    try:
        with open("src/styles.css", "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except:
        print("error")


# Load custom CSS styles
load_css()

st.markdown("""<div class="navbar">
    <div class="dropdown">
        <button class="dropbtn">Home</button>
        <div class="dropdown-content">
            <a href="#">Option 1</a>
            <a href="#">Option 2</a>
            <a href="#">Option 3</a>
        </div>
    </div>
    <a href="#">About</a>
    <a href="#">Services</a>
    <a href="#" class="navbar-right">Login</a>
</div>""", unsafe_allow_html=True)
