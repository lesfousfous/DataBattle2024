import streamlit as st
from main import process_desciption

# Define your Python function that will be executed when the button is clicked


def process_input(input_text):
    # Process the input here (e.g., print it)
    return ("Input:", input_text)


# Streamlit app layout
st.title("Search Bar and Button Example")

# Create a search bar
search_input = st.text_input("Enter your search query:")

session_state = st.session_state
if "output" not in session_state:
    session_state.output = None


# Create a button to trigger the processing function
if st.button("Process"):
    # Call the processing function with the content of the search bar as an argument
    output = process_desciption(search_input)
    session_state.output = output

if session_state.output is not None:
    st.write("Output:", session_state.output)
