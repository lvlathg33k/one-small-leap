import streamlit as st

def render(next_step, prev_step, com_val):
    st.header("Step 4: Asset Reconnaissance")
    st.caption("Enter the current balances of your accounts. If you don't know what an account is, or if you don't have one, simply leave it blank. Hover over the '?' icons for simple explanations.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Liquid Cash")
        st.session_state.ast_checking = st.number_input("Checking Accounts ($)", min_value=0.0, value=st.session_state.ast_checking, help="Where your paycheck lands. Used for paying daily bills.")
        st.session_state.ast_savings = st.number_input("Savings Accounts ($)", min_value=0.0, value=st.session_state.ast_savings, help="Where you park cash for emergencies or short-term goals. Should ideally be a High-Yield Savings Account (HYSA).")
        
        st.subheader("Real Estate")
        st.session_state.ast_home = st.number_input("Home Equity ($)", min_value=0.0, value=st.session_state.ast_home, help="The estimated value of your home MINUS what you still owe on the mortgage.")
        
    with col2:
        st.subheader("Investments & Retirement")
        st.session_state.ast_taxable = st.number_input("Taxable Brokerage ($)", min_value=0.0, value=st.session_state.ast_taxable, help="Standard investment accounts (like Robinhood or Vanguard) that are not protected from taxes.")
        st.session_state.ast_trad_ira = st.number_input("Traditional IRA / 401(k) ($)", min_value=0.0, value=st.session_state.ast_trad_ira, help="Retirement accounts where you put money in pre-tax, but pay taxes when you pull it out in retirement.")
        st.session_state.ast_roth_ira = st.number_input("Roth IRA / Roth 401(k) ($)", min_value=0.0, value=st.session_state.ast_roth_ira, help="Retirement accounts where you pay taxes now, but the money grows and is withdrawn completely tax-free forever.")
        st.session_state.ast_hsa = st.number_input("HSA Balance ($)", min_value=0.0, value=st.session_state.ast_hsa, help="Health Savings Account. Money goes in tax-free, grows tax-free, and comes out tax-free for medical expenses.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    total_cash = (st.session_state.ast_checking or 0) + (st.session_state.ast_savings or 0)
    taxable_investments = st.session_state.ast_taxable or 0
    ef_target = com_val * 3
    
    if total_cash < ef_target and taxable_investments > 0:
        st.warning(f"⚠️ **System Observation:** Your cash safety net is underfunded, but you have \${taxable_investments:,.2f} exposed in taxable market accounts. You may need to liquidate investments to fill your cash moat to \${ef_target:,.2f}.")
        
    c2.button("Next", on_click=next_step, type="primary")
