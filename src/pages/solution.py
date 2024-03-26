import streamlit as st
from utils.design import load_all_page_requirements, show_solution
import random


graph_data = {
    "gainenergie": [
        {
            "coeff_reg": 3.7,
            "unite_energie": "kWh",
            "cost": [13000, 43000],
            "gain": [67000, 78000]
        },
        {
            "coeff_reg": 1.4,
            "unite_energie": "litres",
            "cost": [13000, 43000],
            "gain": [67000, 78000]
        }
    ],
    # "gainGES": [
    #     {
    #         "coeff_reg": 3.7,
    #         "unite_energie": "C02eq",
    #         "cost": [13000, 43000],
    #         "gain": [67000, 78000]
    #     },
    #     {
    #         "coeff_reg": 1.4,
    #         "unite_energie": "litres",
    #         "cost": [13000, 43000],
    #         "gain": [67000, 78000]
    #     }
    # ]
}

load_all_page_requirements()

if 'selected_solutions' not in st.session_state:
    st.session_state['selected_solutions'] = random.sample(
        st.session_state["solutions"], 5)

if 'selected_solution_id' not in st.session_state:
    st.title("Solutions Overview")
    solutions = st.session_state["selected_solutions"]
    for solution in solutions:
        if st.button(solution.get_title()):
            print("Hello")
            st.session_state['current_solution'] = solution
            st.rerun()
if "graph_data" not in st.session_state:
    st.session_state.graph_data = graph_data

show_solution()

if st.button("Back to Solutions List"):
    del st.session_state['current_solution']
    st.rerun()
