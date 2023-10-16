import streamlit as st

# Title
st.title("Hello, World!")

# Text
st.write("This is a simple Streamlit web application.")

# Display an image
st.image("https://www.example.com/your-image.png", caption="Streamlit Logo", use_column_width=True)

# Add a button
if st.button("Click me"):
    st.write("You clicked the button!")

# Add a checkbox
checkbox = st.checkbox("Check this box")
if checkbox:
    st.write("The checkbox is checked!")

# Add a selectbox
option = st.selectbox("Choose an option", ["Option 1", "Option 2", "Option 3"])
st.write("You selected:", option)
