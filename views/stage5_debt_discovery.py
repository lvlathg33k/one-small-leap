import streamlit as st

def render(next_step, prev_step):
    st.header("Step 5: Debt Discovery")
    st.caption("To ensure the math is accurate, verify you have accounted for all potential liabilities. Check each box to confirm you either carry a balance, or verified you have a zero balance for that category.")

    st.session_state.cc_check = st.checkbox("Credit Cards (Chase, Amex, Capital One, Store/Retail cards, etc.)", value=st.session_state.cc_check)
    st.session_state.auto_check = st.checkbox("Auto Loans, Leases, or Recreational Vehicle notes", value=st.session_state.auto_check)
    st.session_state.student_check = st.checkbox("Student Loans (Federal or Private)", value=st.session_state.student_check)
    st.session_state.mortgage_check = st.checkbox("Mortgages, HELOCs, or other real estate loans", value=st.session_state.mortgage_check)
    st.session_state.payday_check = st.checkbox("Payday Loans, Personal Loans, or 'Buy Now, Pay Later' (e.g., Klarna, Affirm, Speedy Cash)", value=st.session_state.payday_check)

    all_checked = (st.session_state.cc_check and st.session_state.auto_check and 
                   st.session_state.student_check and st.session_state.mortgage_check and 
                   st.session_state.payday_check)

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if all_checked:
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Acknowledge all categories to continue", disabled=True)
