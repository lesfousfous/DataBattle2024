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
      background-color: #f9f9f9; /* Light grey background */
    }
    
    .columns {
      
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
    st.markdown(
        f"""
        <div class="container-box">
          <h1 class='title'>{title}<h1>
          <hr class='title-divider'>
          <p>{solution.get_description()}</p>
          <div class='columns'>
            <div class='big-box'><p>{solution.get_difficultes()}</p></div>
            <div class='big-box'><p>{solution.get_application()}</p></div>
          <div>
        </div>
    """, unsafe_allow_html=True
    )
