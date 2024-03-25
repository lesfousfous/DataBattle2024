import streamlit as st
from ..utils import database
import plotly.graph_objects as go


solutions = [SolutionDB(id) for id in [160, 170]]

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
    
    .box-title {
      display: inline-block;
      border-radius: 10px;
      margin-bottom : 0.5em;
      text-align : center;
      border: 2px solid #4CAF50; /* Green border */ 
    }
    .main {
      display : flex;
      align-items : center;
    }
    
    .title-divider {
      border-top: 2px solid #4CAF50; /* Green line */
      width: 100%; /* Full width */
      margin: 10px 0 20px; /* Spacing around the divider */   
    }   
    
    .container-box {
      width : 50vmax;
      border-radius: 10px; /* Rounded corners */
      padding: 40px; /* Padding inside the box */
      background-color: #394045; /* Light grey background */
    }
    
    .champs {
        display: grid; /* Establishes a grid container */
        grid-template-rows: auto; /* Defines column sizes */
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
    
    .cout-table {
      display : grid
      grid-template-rows: auto; /* Defines column sizes */
      gap: 10px; /* Space between rows and columns */
      justify-content: start; /* aligns the grid along the row axis */
      align-content: start; /* aligns the grid along the column axis */
      grid-auto-flow: row; /* Controls how auto-placed items get inserted in the grid */
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
      }

      th, td {
        border: 1px solid black;
        padding: 8px;
        text-align: left;
      }
      
      .green {
        background-color : green
      }
      
      .red {
        background-color : red
      }
      td {
        height : 20px
      }
      
      .application, .bilan-ener {
        border: 2px solid #2a88f5; /* Blue border */ 
      }
      
      .application .box-title, .bilan-ener .box-title {
        border: 2px solid #2a88f5; /* Blue border */ 
        color : #2a88f5;
      }
    }

    
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
    title = f"Solution {solution.get_id()} : {solution.get_title()}"
    boxes = []
    text_data = [("Application", solution.get_application(), "application"),
                 ("Bilan Energétique", solution.get_bilan_energie(), "bilan-ener")]
    for name, text, class_name in text_data:
        if text != "Aucune":
            boxes.append(f"""<div class='big-box {class_name}'>
              <h3 class='title box-title'>{name}</h3>
              <p>{text}</p>
            </div>""")

    plus = "".join(["+" for x in range(int(solution.get_regle_pouce_gain()))])
    moins = "".join(["-" for x in range(int(solution.get_regle_pouce_cout()))])

    regle_du_pouce = "".join(plus)

    difficultes = f"""
    <h5>Difficultés :</h5>
    <span>{solution.get_difficultes()}</span>
    """
    effets_positifs = f"""
    <h5>Effets positifs :</h5>
    <span>
      {solution.get_effets_positifs()}
    </span>
    """

    gain_text = f"""
    <h5>Gain de la solution</h5>
    <span>
      {solution.get_gain_text()}
    </span>
    """

    cout_text = f"""
    <h5>Coût de la solution</h5>
    <span>
      {solution.get_cout_text()}
    </span>
    """
    table = f"""
    <table>
      <tr>
        <th class='green'>Gains</th>
        <th class='red'>Coûts</th>
      </tr>
      <tr>
        <td>{plus}</td>
        <td>{moins}</td>
      </tr>
      <tr>
        <td>{effets_positifs}</td>
        <td>{difficultes}</td>
      </tr>
      <tr>
        <td>{gain_text}</td>
        <td>{cout_text}</td>
      </tr>
    </table>
    """

    boxes.append(f"""<div class='big-box'>
              <h3 class='title box-title'>Synthèse économique</h3>
              <div>{table}</div>
            </div>""")
    st.markdown(
        f"""
        <div class="container-box">
          <h1 class='title'>{title}</h1>
          <hr class='title-divider'>
          <p>{solution.get_description()}</p>
          <div class='champs'>
            {"".join(boxes)}
          </div>
        </div>
    """, unsafe_allow_html=True
    )
    # Create a Plotly graph
    fig = go.Figure(data=go.Bar(y=[2, 3, 1]))

    # Display the Plotly graph in Streamlit
    st.plotly_chart(fig)
    link = st.button("Back")
    if link:
        st.session_state.show_details = False
