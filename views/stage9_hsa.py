import streamlit as st

def render(next_step, prev_step):
    st.header("Step 9: The HSA Gateway")
    st.caption("Health Savings Accounts are triple-tax-advantaged (tax-free in, tax-free growth, tax-free out). We need to see if you qualify to use one.")
    
    st.session_state.hdhp_status = st.radio(
        "Are you currently enrolled in a High-Deductible Health Plan (HDHP) at work?", 
        ["Select...", "Yes, I have an HDHP", "No, I have a standard plan (PPO, HMO, etc.)"]
    )
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.hdhp_status == "Select...":
        c2.button("Make a selection to continue", disabled=True)
    else:
        if st.session_state.hdhp_status == "Yes, I have an HDHP":
            st.success("💡 Excellent. You have access to the ultimate tax loophole. Your wealth generation waterfall on the next page will prioritize maxing out your HSA before your IRA. Remember: DO NOT spend your HSA money on medical bills right now. Pay cash, keep the receipts, and let the HSA money grow in the stock market.")
        else:
            st.info("💡 Understood. Because you are not in an HDHP, you cannot utilize an HSA. Your wealth generation waterfall will skip directly to your Roth IRA and 401(k).")
        c2.button("Next", on_click=next_step, type="primary")
