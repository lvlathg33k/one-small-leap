import streamlit as st

def render(next_step, prev_step):
    st.header("Step 1: Cash Flow")
    st.caption("Let's establish your baseline. We need to know exactly how much cash hits your bank account every month.")
    st.session_state.take_home = st.number_input(
        "Monthly Net Take-Home Pay ($)", 
        min_value=0.0, 
        step=100.0, 
        value=st.session_state.take_home, 
        help="Look at your paystub. Find the 'Net Pay' (what actually lands in your checking account after taxes and deductions). Scale that to a monthly number."
    )
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    if st.session_state.take_home is not None and st.session_state.take_home > 0:
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Enter your income to continue", disabled=True)
