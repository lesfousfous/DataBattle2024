import streamlit as st

# Define your Python function that will be executed when the button is clicked
def process_input(input_text):
    # Process the input here (e.g., print it)
    return ("Input:", input_text)

# Streamlit app layout
st.title("Search Bar and Button Example")

# Create a search bar
search_input = st.text_input("Enter your search query:")

# Create a button to trigger the processing function
if st.button("Process"):
    # Call the processing function with the content of the search bar as an argument
    output = process_input(search_input)
    st.write(output)