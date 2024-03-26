import streamlit as st
from utils.run_part1 import process_description
from utils.database import SolutionDB
import random
# from streamlit_main_page import load_css

from utils.design import load_css, nav_bar

load_css()
nav_bar(st.session_state["solutions"])


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

# Function to display results


def display_results(category, relevant_solutions):
    if category is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.header(f"Catégorie : {category.get_name()}")
            st.markdown("""<p class='category-text'>Nous avons trouvé que votre demande correspond probablement à la catégorie ci-dessus, 
                        voici quelques solutions tirées au hasard de cette catégorie : <p>""", unsafe_allow_html=True)
            solutions_in_category = category.get_solutions()
            random_picked = random.sample(
                range(len(solutions_in_category)), min(3, len(solutions_in_category)))
            solutions_random = [solutions_in_category[i]
                                for i in random_picked]
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


load_css()
st.title("Make a query")

search_input = st.text_input("Enter your search query:")

# Initialize session state variables if they don't exist
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'last_results' not in st.session_state:
    st.session_state.last_results = None
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

if 'nb' not in st.session_state:
    st.session_state.nb = 0
# Button to initiate processing
if st.button("Process", disabled=st.session_state.processing) or st.session_state.processing:
    st.session_state.nb += 1
    print(st.session_state.nb)
    print(f"Processing : {st.session_state.processing}\nLast Results : {st.session_state.last_results}\nDisabled : {st.session_state.button_disabled}")
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

# if st.session_state.process_clicked and not st.session_state.processing:
#     st.session_state.processing = True
#     category, relevant_solutions = process_description(search_input)
#     if category is not None:

#         col1, col2 = st.columns(2)
#         with col1:
#             st.header(f"Catégorie : {category.get_name()}")
#             st.markdown(
#                 """<p class='category-text'>Nous avons trouvé que votre demande correspond probablement à la catégorie ci-dessus,
#                 voici quelques solutions tirées au hasard de cette catégorie : <p>""", unsafe_allow_html=True)
#             # Display first 3 solutions for the technology
#             solutions_in_category = category.get_solutions()
#             random_picked = random.sample(range(len(solutions_in_category)), 3)
#             solutions_random = [solutions_in_category[i]
#                                 for i in random_picked]
#             for solution in solutions_random:
#                 display_solution(solution)

#         with col2:
#             st.header("Solutions")
#             st.markdown(
#                 """<p class='category-text'>Voici les solutions les plus proches de votre demande : <p>""", unsafe_allow_html=True)
#             for solution in relevant_solutions:
#                 display_solution(solution)
#     else:
#         st.header("Solutions")
#         for solution in relevant_solutions:
#             display_solution(solution)
#     st.session_state.process_clicked = False
#     st.session_state.processing = False
#     st.rerun()
