import streamlit as st

def render(next_step, prev_step, margin):
    st.header("Step 3: Baseline Expenses")
    st.caption("What absolutely must leave your account every month to keep the lights on? **DO NOT include large, multi-month expenses here** (like annual car registration or Christmas). We will factor those in later. Only include strict monthly minimums (rent, groceries, utilities, minimum debt payments).")
    
    st.session_state.base_committed = st.number_input(
        "Monthly Baseline Committed Bills ($)", 
        min_value=0.0, 
        step=100.0, 
        value=st.session_state.base_committed
    )
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.base_committed is not None:
        if margin <= 0:
            st.error("🚨 **Your One Next Step: Stop the Bleeding**\n\nYour basic bills exceed or equal your income. You are mathematically underwater.\n\n**Action Required:** Leave this app right now. Cancel subscriptions, negotiate bills, or take on extra income. You cannot proceed until you change the 'Committed Bills' input above to generate a positive margin.")
            c2.button("Fix deficit to continue", disabled=True)
        else:
            c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Enter your expenses to continue", disabled=True)
