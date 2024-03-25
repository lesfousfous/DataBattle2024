import streamlit as st
from database import SolutionDB

solutions = [SolutionDB(id) for id in range(260, 265)]

# Initialize session state
if "show_details" not in st.session_state:
    st.session_state.show_details = False
if "current_solution" not in st.session_state:
    st.session_state.current_solution = {}


def show_solution_details(solution: SolutionDB):
    """Callback function to show solution details."""
    st.session_state.current_solution = solution
    st.session_state.show_details = True


# Main page layout
if not st.session_state.show_details:
    st.title("Solutions")
    for solution in solutions:
        link = st.button(solution.get_title())
        if link:
            show_solution_details(solution)
else:
    solution: SolutionDB
    solution = st.session_state.current_solution
    # Custom CSS to style the boxes
    custom_css = """
    <style>
    .title {
      color : #73BE31
    }
    
    .title-divider {
      border-top: 2px solid #4CAF50; /* Green line */
      width: 100%; /* Full width */
      margin: 10px 0 20px; /* Spacing around the divider */   
    }   
    
    .container-box {
      border: 2px solid #4CAF50; /* Green border */
      border-radius: 10px; /* Rounded corners */
      padding: 20px; /* Padding inside the box */
      margin: 20px 0; /* Margin outside the box */
      background-color: #394045; /* Light grey background */
    }
    
    .columns {
        display: grid; /* Establishes a grid container */
        grid-template-columns: 50% auto; /* Defines column sizes */
        gap: 10px; /* Space between rows and columns */
        justify-content: start; /* aligns the grid along the row axis */
        align-content: start; /* aligns the grid along the column axis */
        grid-auto-flow: row; /* Controls how auto-placed items get inserted in the grid */
    }
    
       /* Style for the detail boxes */
    .big-box {
        border: 2px solid #4CAF50; /* Green border */
        border-radius: 5px; /* Rounded corners */
        padding: 20px; /* Some padding */
        margin: 20px 0; /* Some margin */
    }
    /* Optional: Style for the text inside boxes */
    .big-box p {
        font-size: 20px; /* Larger text */
    }
    
    
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
    title = f"{solution.get_title()}"
    boxes = []
    text_data = [("Description", solution.get_description()),
                 ("Difficultés", solution.get_difficultes()),
                 ("Effets positifs", solution.get_regle_pouce_text()),
                 ("Règle du pouce", solution.get_regle_pouce_text()),
                 ("Bilan Energie", solution.get_bilan_energie())]
    for name, text in text_data:
        if text != "Aucune":
            boxes.append(f"""<div class='big-box'>
              <h3 class='title'>{name}<h3>
              <p>{text}</p>
            </div>""")
    st.markdown(
        f"""
        <div class="container-box">
          <h1 class='title'>{title}<h1>
          <hr class='title-divider'>
          <p>{solution.get_description()}</p>
          <div class='columns'>
            {"".join(boxes)}
          <div>
        </div>
    """, unsafe_allow_html=True
    )
    link = st.button("Back")
    if link:
        st.session_state.show_details = False
