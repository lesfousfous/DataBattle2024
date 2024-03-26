import streamlit as st
from utils.run_part1 import process_description
from utils.database import SolutionDB, Category
import random
# from streamlit_main_page import load_css


def load_css():
    try:
        with open("src/styles.css", "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except:
        print("error")


def cut_text(text, length):
    if text == "Aucune":
        return "Aucune description disponible"
    if len(text) > length:
        return text[:length] + "..."

    return text


def display_solution(solution: SolutionDB):
    st.markdown(f"""
                <div class='sol-preview'>
                  <h5>{solution.get_title()}</h5>
                  <p>{cut_text(solution.get_description(), 150)}
                </div>
    """, unsafe_allow_html=True)


load_css()
st.title("Make a query")

search_input = st.text_input("Enter your search query:")

session_state = st.session_state
if "output" not in session_state:
    session_state.output = None


if st.button("Process"):
    category, relevant_solutions = process_description(search_input)
    if category is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.header(f"Catégorie : {category.get_name()}")
            # Display first 3 solutions for the technology
            solutions_in_category = category.get_solutions()
            random_picked = random.sample(range(len(solutions_in_category)), 3)
            solutions_random = [solutions_in_category[i]
                                for i in random_picked]
            for solution in solutions_random:
                display_solution(solution)

        with col2:
            st.header("Solutions")
            for solution in relevant_solutions:
                display_solution(solution)
    else:
        st.header("Solutions")
        for solution in relevant_solutions:
            display_solution(solution)
