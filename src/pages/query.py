import streamlit as st
from utils.run_part1 import process_description
from utils.database import SolutionDB
from utils.design import load_all_page_requirements, show_solution
from streamlit.errors import DuplicateWidgetID
import random


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
    try:
        if st.button("Accèder à la solution", key=f"button_{solution.get_id()}"):
            st.session_state['selected_solution_id'] = solution.get_id()
            st.rerun()

    except DuplicateWidgetID:
        if st.button("Accèder à la solution", key=f"button_{(solution.get_id() + 1)*10000}"):
            st.session_state['selected_solution_id'] = solution.get_id()
            st.rerun()


# Function to display results


def display_results(category, relevant_solutions):
    if category is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.header(f"Catégorie : {category.get_name()}")
            st.markdown("""<p class='category-text'>Nous avons trouvé que votre demande correspond probablement à la catégorie ci-dessus, 
                        voici quelques solutions tirées au hasard de cette catégorie : <p>""", unsafe_allow_html=True)
            solutions_in_category = category.get_solutions()
            solutions_random = [
                solution for solution in solutions_in_category[:3]]
            solutions_random = random.sample(solutions_in_category, 3)
            for solution in solutions_random:
                display_solution(solution)

        with col2:
            st.header("Solutions")
            st.markdown(
                """<p class='category-text'>Voici les solutions les plus proches de votre demande : <p>""", unsafe_allow_html=True)
            for solution in relevant_solutions:
                display_solution(solution)
    else:
        st.header("Solutions")
        for solution in relevant_solutions:
            display_solution(solution)


def show_query_page():

    st.title("Entrez votre demande")

    search_input = st.text_input("Entrez votre demande :")

    # Initialize session state variables if they don't exist
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_results' not in st.session_state:
        st.session_state.last_results = None
    if 'button_disabled' not in st.session_state:
        st.session_state.button_disabled = False

    # Button to initiate processing
    if st.button("Chercher", disabled=st.session_state.processing) or st.session_state.processing:
        st.session_state.processing = True
        if not st.session_state.button_disabled:
            st.session_state.button_disabled = True
            st.rerun()
        # Perform the processing
        category, relevant_solutions = process_description(search_input)
        # Store the results in session state
        st.session_state.last_results = (category, relevant_solutions)
        st.session_state.processing = False
        st.rerun()

    # Display last results if they exist
    if st.session_state.last_results:
        st.session_state.button_disabled = False
        display_results(*st.session_state.last_results)


load_all_page_requirements()


# Handling the action when a solution is selected
if 'selected_solution_id' in st.session_state:
    show_solution()
    if st.button("Retourner à la page de demande"):
        del st.session_state.selected_solution_id
        st.rerun()
else:

    show_query_page()
