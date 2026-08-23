import streamlit as st

def render(next_step, prev_step):
    st.header("Step 2: The Employer Match")
    st.caption("Before we calculate anything else, we must check for free money.")
    st.session_state.employer_match = st.radio(
        "Are you currently capturing 100% of your employer's 401(k) match?", 
        ["Select...", "Yes / My employer offers no match", "No, I am leaving match money on the table"]
    )
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.employer_match == "No, I am leaving match money on the table":
        st.warning("⚠️ **Your One Next Step: Capture Free Money**\n\nYour employer is offering you a guaranteed 100% return, and you are actively ignoring it.\n\n**Action Required:** Leave this app right now. Log into your HR portal and increase your contribution to the exact match limit. Once completed, return here and change your answer to unlock the system.")
    elif st.session_state.employer_match == "Yes / My employer offers no match":
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Make a selection to continue", disabled=True)
