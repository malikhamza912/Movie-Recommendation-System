import streamlit as st

def run():
    st.title("Test App")
    if st.button("Click me"):
        st.write("Button clicked!")

if __name__ == '__main__':
    run()