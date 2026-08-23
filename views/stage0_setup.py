import streamlit as st

def render(next_step, prev_step):
    st.title("One Small Leap")
    st.caption("This system mathematically prioritizes your capital. It does not give suggestions; it issues operational directives. We take action to overcome overthinking.")
    st.session_state.household = st.radio("Household Architecture:", ["Single Operator", "Married (Joint Finances)"])
    st.button("Begin", on_click=next_step, type="primary")
