import streamlit as st
import plotly.graph_objects as go
from utils.database import SolutionDB, DatabaseObject
import numpy as np
from utils.regression import predict


def load_css():
    try:
        with open("src/styles.css", "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except:
        print("error")


def nav_bar():
    options_str = ""
    categories = set([])
    solutions = st.session_state.solutions
    for solution in solutions:

        first_category = solution.get_category().get_technologies()
        count = 0
        if len(first_category) > 1:

            (first_category_name, first_category_id) = (
                first_category[1].get_name(), first_category[1].get_id())
            if not first_category_id in categories:
                count += 1
                categories.add(first_category_id)
                options_str += '<button class="option" id="' + \
                    str(count) + '">' + first_category_name + '</button>'

    st.markdown("""<div class="navbar">
        <div class="dropdown">
            <button class="dropbtn">Home</button>
            <div class="dropdown-content">
                """ + options_str + """
            </div>
        </div>
        <a href="#">About</a>
        <a href="#">Services</a>
        <a href="#" class="navbar-right">Login</a>
    </div>
    <div class="submenu" id="1">
        <a href="#">Subcategory 1 Option 1</a>
        <a href="#">Subcategory 1 Option 2</a>
        <a href="#">Subcategory 1 Option 3</a>
    </div><div class="submenu" id="1">
        <a href="#">Subcategory 1 Option 1</a>
        <a href="#">Subcategory 1 Option 2</a>
        <a href="#">Subcategory 1 Option 3</a>
    </div>
    """, unsafe_allow_html=True)


def load_all_page_requirements():
    if "set_page_config" not in st.session_state:
        st.set_page_config(layout="wide")
        st.session_state.set_page_config = True

    if "solutions" not in st.session_state:
        DatabaseObject.cursor.execute(
            f"""SELECT numsolution FROM tblsolution""")
        solution_ids = [x[0] for x in DatabaseObject.cursor.fetchall()]
        solutions = [SolutionDB(id) for id in solution_ids]
        st.session_state["solutions"] = solutions
    load_css()
    nav_bar()


def show_solution():
    solution: SolutionDB
    solution = [solution for solution in st.session_state.solutions if solution.get_id(
    ) == st.session_state.selected_solution_id][0]
    graph_data = predict(solution.id)
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
    plot_graph(graph_data)


def load_cout_gain_table_into_html(solution: SolutionDB):
    if solution.get_regle_pouce_gain() != "Aucune":
        plus = "".join(
            ["+" for x in range(int(solution.get_regle_pouce_gain()))])
        moins = "".join(
            ["-" for x in range(int(solution.get_regle_pouce_cout()))])
    else:
        plus = ""
        moins = ""

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


# def plot_graph(graph_data: dict):
#     for key, value in graph_data.items():
#         isEnergy = False
#         if value is None:  # Don't plot the graph if no data is available
#             continue
#         category_name = key
#         if category_name == "energy":
#             category_name = "Gain Energétique"
#             color = '#4CAF50'
#             isEnergy = True
#         elif category_name == "financial":
#             category_name = "Gain Financier"
#             color = 'RoyalBlue'
#         elif category_name == "greenhouse":
#             category_name = "Réduction des émissions"
#             color = "#a83832"
#         if not isEnergy:
#             pente, ordonnee = value["a"], value["b"]
#             unite_gain, unite_cout = value["unit_gain"], value["unit_cost"]
#             cost_values = value["cost"]
#             gain_values = value["gain"]

#             scatter = go.Scatter(x=cost_values, y=gain_values,
#                                  mode='markers',  # Only markers for data points
#                                  name='Data Points',
#                                  marker=dict(color=color, size=12))

#             fig = go.Figure(data=scatter)

#             x = np.linspace(0, max(cost_values)*1.25, 25)
#             # Adding Cost Line
#             fig.add_trace(go.Scatter(x=x, y=pente*x + ordonnee,
#                                      mode='lines+markers',
#                                      name=f'Gain',

#                                      line=dict(color=color)))

#             # Updating layout for each figure
#             fig.update_layout(title=f'{category_name} en {unite_gain}',
#                               xaxis_title=f'Coût en {unite_cout}',
#                               yaxis_title=f'Gain en {unite_gain}',
#                               legend_title='Légende')
#             st.plotly_chart(fig)
#         else:
#             cols = st.columns(len(value))
#             for energy_data, col in zip(value, cols):
#                 pente, ordonnee = energy_data["a"], energy_data["b"]
#                 unite_gain, unite_cout = energy_data["unit_gain"], energy_data["unit_cost"]
#                 cost_values = energy_data["cost"]
#                 gain_values = energy_data["gain"]

#                 scatter = go.Scatter(x=cost_values, y=gain_values,
#                                      mode='markers',  # Only markers for data points
#                                      name='Data Points',
#                                      marker=dict(color=color, size=12))

#                 fig = go.Figure(data=scatter)

#                 x = np.linspace(0, max(cost_values)*1.25, 25)
#                 # Adding Cost Line
#                 fig.add_trace(go.Scatter(x=x, y=pente*x + ordonnee,
#                                          mode='lines+markers',
#                                          name=f'Gain',
#                                          line=dict(color=color)))

#                 # Updating layout for each figure
#                 fig.update_layout(title=f'{category_name} in {unite_gain}',
#                                   xaxis_title=f'Cost in {unite_cout}',
#                                   yaxis_title=f'Energy in {unite_gain}',
#                                   legend_title='Legend')
#                 with col:
#                     st.plotly_chart(fig)

def plot_graph(graph_data: dict):
    for key, value in graph_data.items():
        if value is None:  # Don't plot the graph if no data is available
            continue

        # Define category properties
        category_properties = {
            "energy": {"name": "Gain Energétique", "color": '#4CAF50'},
            "financial": {"name": "Gain Financier", "color": 'RoyalBlue'},
            "greenhouse": {"name": "Réduction des émissions", "color": "#a83832"}
        }

        category_name = category_properties[key]["name"]
        color = category_properties[key]["color"]

        # Plotting
        for energy_data in value if key == "energy" else [value]:
            scatter = go.Scatter(x=energy_data["cost"], y=energy_data["gain"],
                                 mode='markers',  # Only markers for data points
                                 name='Data Points',
                                 marker=dict(color=color, size=12))

            fig = go.Figure(data=scatter)

            x = np.linspace(0, max(energy_data["cost"])*1.25, 25)
            # Adding Cost Line
            fig.add_trace(go.Scatter(x=x, y=energy_data["a"]*x + energy_data["b"],
                                     mode='lines+markers',
                                     name='Gain',
                                     line=dict(color=color)))

            # Updating layout for each figure
            fig.update_layout(title=f'{category_name} in {energy_data["unit_gain"]}',
                              xaxis_title=f'Cost in {energy_data["unit_cost"]}',
                              yaxis_title=f'Energy in {energy_data["unit_gain"]}',
                              legend_title='Legend')

            st.plotly_chart(fig, use_container_width=True)  # Center the plot
