import streamlit as st
import pandas as pd
import datetime
import math

def render(next_step, prev_step, reset, margin):
    st.header("Step 10: The Wealth Engine")
    st.caption("You have survived the gauntlet. You have zero toxic debt, a fully funded safety net, and automated sinking funds. It is time to deploy your unallocated margin into wealth generation.")
    
    st.markdown("### The Capital Allocation Waterfall")
    st.markdown("Do not skip steps. Max out the limit on one tier before deploying capital to the next. *This assumes you are already capturing your 401(k) match as established in Step 2.*")
    
    if st.session_state.hdhp_status == "Yes, I have an HDHP":
        st.markdown("1. **Health Savings Account (HSA):** Max this out. Invest it in broad-market funds. Do not spend it on current medical bills.")
        st.markdown("2. **Roth IRA:** Max out statutory limits ($7,000/yr). Invest in low-cost factor-tilt index funds (e.g., small-cap value).")
        st.markdown("3. **Max 401(k):** Return to your employer plan and fill it to the $23,500 maximum.")
        st.markdown("4. **Taxable Brokerage:** Deploy all remaining margin into standard brokerage ETFs.")
    else:
        st.markdown("1. **Roth IRA:** Max out statutory limits ($7,000/yr). Invest in low-cost factor-tilt index funds (e.g., small-cap value).")
        st.markdown("2. **Max 401(k):** Return to your employer plan and fill it to the $23,500 maximum.")
        st.markdown("3. **Taxable Brokerage:** Deploy all remaining margin into standard brokerage ETFs.")

    st.divider()
    st.subheader("Goal Trajectory Modeling")
    st.caption("Money without direction is wasted. Set a specific goal. We map the timeline assuming a conservative 7% real annualized return.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.goal_name = st.text_input("Target Objective", value=st.session_state.goal_name, placeholder="e.g. 20% House Down Payment")
    with col2:
        st.session_state.goal_target = st.number_input("Target Capital Required ($)", min_value=0.0, step=1000.0, value=st.session_state.goal_target)
    
    if margin > 0 and st.session_state.goal_target and st.session_state.goal_name:
        annual_rate = 0.07
        monthly_rate = annual_rate / 12
        try:
            n_months = math.ceil(math.log((st.session_state.goal_target * monthly_rate / margin) + 1) / math.log(1 + monthly_rate))
        except:
            n_months = int(st.session_state.goal_target // margin) + 1
            
        years = n_months // 12
        rem_months = n_months % 12
        time_str = f"{years} yr, {rem_months} mo" if years > 0 else f"{rem_months} months"
        
        st.success(f"🎯 **Trajectory Locked:** By investing your **\${margin:,.2f}** monthly margin at 7%, you will achieve **\${st.session_state.goal_target:,.2f}** in **{time_str}**.")
        
        timeline_data = []
        current_date = datetime.date.today()
        accumulated = 0
        for m in range(n_months + 1):
            if m > 0: accumulated = (accumulated + margin) * (1 + monthly_rate)
            timeline_data.append({"Date": current_date + pd.DateOffset(months=m), "Capital ($)": min(accumulated, st.session_state.goal_target)})
            
        st.line_chart(pd.DataFrame(timeline_data).set_index("Date"))

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("🔄 Restart Audit", on_click=reset)
