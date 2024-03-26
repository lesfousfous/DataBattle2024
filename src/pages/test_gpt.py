import pandas as pd
import streamlit as st
from utils.database import SolutionDB
import plotly.graph_objects as go
import numpy as np


def load_cout_gain_table_into_html(solution: SolutionDB):
    plus = "".join(["+" for x in range(int(solution.get_regle_pouce_gain()))])
    moins = "".join(["-" for x in range(int(solution.get_regle_pouce_cout()))])

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

    return f"""<div class='big-box'>
              <h3 class='title box-title'>Synthèse économique</h3>
              <div>{table}</div>
            </div>"""


def plot_graph(category, entries):
    for entry in entries:
        category_name = category
        if category == "gainenergie":
            category_name = "Gain Energétique"
        elif category == "gainfinancier":
            category_name = "Gain Financier"
        coeff_reg = entry["coeff_reg"]
        unite_energie = entry["unite_energie"]
        cost = entry["cost"]
        gain = entry["gain"]
        scatter = go.Scatter(x=cost, y=gain,
                             mode='markers',  # Only markers for data points
                             name='Data Points',
                             marker=dict(color='RoyalBlue', size=12))

        fig = go.Figure(data=scatter)

        x = np.linspace(0, 100000, 25)
        # Adding Cost Line
        fig.add_trace(go.Scatter(x=x, y=coeff_reg*x,
                                 mode='lines+markers',
                                 name=f'Gain'))

        # Updating layout for each figure
        fig.update_layout(title=f'{category_name}',
                          xaxis_title='Cost',
                          yaxis_title=f'Energy in {unite_energie}',
                          legend_title='Legend')
        st.plotly_chart(fig)


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
    
    
    .title-divider {
      border-top: 2px solid #4CAF50; /* Green line */
      width: 100%; /* Full width */
      margin: 10px 0 20px; /* Spacing around the divider */   
    }   
    
    .block-container {
      border-radius: 20px; /* Rounded corners */
      background-color: #394045; /* Light grey background */
      padding : 30px 20px 0 20px
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

solutions = [SolutionDB(id) for id in [160, 170]]

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


st.title("Solutions Overview")

for solution in solutions:
    if st.button(solution.get_title()):
        st.session_state['current_solution'] = solution
        st.rerun()
if 'current_solution' in st.session_state:
    solution: SolutionDB
    solution = st.session_state['current_solution']
    st.markdown(custom_css, unsafe_allow_html=True)
    print(solution)
    title = f"Solution {solution.get_id()} : {solution.get_title()}"
    st.markdown(f"<h1 class='title'>{title}</h1>", unsafe_allow_html=True)
    st.markdown("<hr class='title-divider'>", unsafe_allow_html=True)
    st.markdown(solution.get_description(), unsafe_allow_html=True)
    st.markdown(f"""<div class='big-box application'>
              <h3 class='title box-title'>Application</h3>
              <p>{solution.get_application()}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='big-box bilan-ener'>
              <h3 class='title box-title'>Bilan Energétique</h3>
              <p>{solution.get_bilan_energie()}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown(load_cout_gain_table_into_html(
        solution), unsafe_allow_html=True)

    # Plotly Graph Example
    for category, entries in graph_data.items():
        plot_graph(category, entries)

    if st.button("Back to Solutions List"):
        del st.session_state['current_solution']
        st.rerun()

# Use this style block to customize the appearance of your Streamlit widgets and layout
