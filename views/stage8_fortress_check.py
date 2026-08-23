import streamlit as st

def render(next_step, prev_step, com_val, margin):
    st.header("Step 8: The Fortress Check")
    st.caption("We must verify your baseline liquidity before exposing your cash to the market.")
    
    ef_target = com_val * 3
    total_cash = (st.session_state.ast_checking or 0) + (st.session_state.ast_savings or 0)
    
    st.markdown(f"**Your 3-Month Survival Target:** \${ef_target:,.2f}")
    st.markdown(f"**Your Current Liquid Cash:** \${total_cash:,.2f}")
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if total_cash < ef_target:
        st.error(f"🛡️ **Your One Next Step: Build the Fortress**\n\nYour safety net is incomplete. You must route 100% of your margin into a High-Yield Savings Account until this vault is full.\n\n**Action Required:** Leave this app. Automate a **\${margin:,.2f}** monthly transfer to your savings account. Return to Step 4 and update your cash balance once it hits \${ef_target:,.2f}.")
        c2.button("Fill Fortress to Proceed", disabled=True)
    else:
        st.success("✅ Your Fortress is fully funded. You are cleared for wealth generation.")
        c2.button("Next", on_click=next_step, type="primary")
