import streamlit as st

from utils.database import DatabaseObject, SolutionDB


def load_css():
    try:
        with open("src/styles.css", "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except:
        print("error")

def nav_bar():
    DatabaseObject.cursor.execute(
            f"""SELECT numsolution FROM tblsolution""")
    solution_ids = [x[0] for x in DatabaseObject.cursor.fetchall()]
    solutions = [SolutionDB(id) for id in solution_ids]
    
    options_str = ""
    categories = set([])
    for solution in solutions:
        
            first_category = solution.get_category().get_technologies()
            if len(first_category) > 1:
                 
                (first_category_name, first_category_id) = (first_category[1].get_name(), first_category[1].get_id())
                if not first_category_id in categories:
                    categories.add(first_category_id)
                    options_str += '<a href="#">' + first_category_name + '</a>'
            
            
        
    
    
    st.markdown("""<div class="navbar">
        <div class="dropdown">
            <button class="dropbtn">Home</button>
            <div class="dropdown-content">
                """ + options_str + """"
            </div>
        </div>
        <a href="#">About</a>
        <a href="#">Services</a>
        <a href="#" class="navbar-right">Login</a>
    </div>""", unsafe_allow_html=True)
