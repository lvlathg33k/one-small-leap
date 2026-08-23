import streamlit as st
import pandas as pd
import datetime
import math

# Configure the application layout
st.set_page_config(page_title="One Small Leap", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 0
if 'household' not in st.session_state: st.session_state.household = "Single"
if 'take_home' not in st.session_state: st.session_state.take_home = None
if 'committed' not in st.session_state: st.session_state.committed = None
if 'employer_match' not in st.session_state: st.session_state.employer_match = "No / I already get the full match"
if 'savings' not in st.session_state: st.session_state.savings = None
if 'debt_df' not in st.session_state: 
    st.session_state.debt_df = pd.DataFrame(columns=["Debt Name", "Balance ($)", "APR (%)", "Min Payment ($)"])
if 'sinking_df' not in st.session_state: 
    st.session_state.sinking_df = pd.DataFrame(columns=["Expense Name", "Total Cost ($)", "Frequency", "Months Until Due"])
if 'has_dependents' not in st.session_state: st.session_state.has_dependents = "No"
if 'income_gap' not in st.session_state: st.session_state.income_gap = None
if 'term_years' not in st.session_state: st.session_state.term_years = 20
if 'goal_name' not in st.session_state: st.session_state.goal_name = ""
if 'goal_target' not in st.session_state: st.session_state.goal_target = None

# Checkbox trackers
if 'cc_check' not in st.session_state: st.session_state.cc_check = False
if 'auto_check' not in st.session_state: st.session_state.auto_check = False
if 'student_check' not in st.session_state: st.session_state.student_check = False
if 'mortgage_check' not in st.session_state: st.session_state.mortgage_check = False
if 'payday_check' not in st.session_state: st.session_state.payday_check = False
if 'ack_match' not in st.session_state: st.session_state.ack_match = False
if 'ack_toxic' not in st.session_state: st.session_state.ack_toxic = False
if 'ack_ef' not in st.session_state: st.session_state.ack_ef = False

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1
def reset(): 
    for key in st.session_state.keys():
        del st.session_state[key]

# ==========================================
# SIDEBAR: PERSISTENT COMMAND SNAPSHOT
# ==========================================
th_val = st.session_state.take_home or 0.0
com_val = st.session_state.committed or 0.0
margin = th_val - com_val

with st.sidebar:
    st.header("Your Snapshot")
    
    st.markdown(f"**Total Take-Home**<br><span style='color: #4da6ff; font-size: 24px; font-weight: bold;'>\${th_val:,.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Committed Money**<br><span style='color: #cc0000; font-size: 24px; font-weight: bold;'>\${com_val:,.2f}</span>", unsafe_allow_html=True)
    
    margin_color = "#00cc44" if margin > 0 else "#ff3333"
    margin_label = "Guilt-Free Margin" if margin > 0 else "Liquidity Deficit"
    st.markdown(f"**{margin_label}**<br><span style='color: {margin_color}; font-size: 24px; font-weight: bold;'>\${margin:,.2f}</span>", unsafe_allow_html=True)
    
    st.divider()
    total_steps = 6
    st.progress(min((st.session_state.step) / total_steps, 1.0))
    st.caption(f"Stage {st.session_state.step} of {total_steps}")

# ==========================================
# MAIN UI: THE WIZARD FLOW
# ==========================================

# STAGE 0: SETUP
if st.session_state.step == 0:
    st.title("One Small Leap")
    st.caption("Most financial platforms shame you for small daily expenses without providing a structured system. This application audits your baseline, mathematically prioritizes your debt and reserves, and outputs your single next operational action.")
    st.session_state.household = st.radio("Household Setup:", ["Single", "Married (Joint Finances)"])
    st.button("Begin", on_click=next_step, type="primary")

# STAGE 1: CASH FLOW & THE FIRST GATES
elif st.session_state.step == 1:
    st.header("Step 1: Enter your income and minimum bills.")
    st.caption("This establishes your baseline. We need to know exactly how much cash hits your bank account, and what absolutely must leave to keep the lights on. Do not include extra debt payments or savings here, just the bare minimums.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.take_home = st.number_input("Monthly Net Take-Home Pay ($)", min_value=0.0, step=100.0, value=st.session_state.take_home, placeholder="e.g. 5000")
        st.markdown("### ")
        st.session_state.employer_match = st.radio(
            "Does your employer offer a 401(k) / retirement match you are NOT currently capturing?", 
            ["No / I already get the full match", "Yes, I am leaving match money on the table"]
        )

    with col2:
        st.session_state.committed = st.number_input("Monthly Baseline Committed Bills ($)", min_value=0.0, step=100.0, value=st.session_state.committed, placeholder="e.g. 3500")
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    # HARD STOP LOGIC
    if st.session_state.take_home is not None and st.session_state.committed is not None:
        if margin <= 0:
            st.error("🚨 **HARD STOP: LIQUIDITY CRISIS**\n\nYour fixed bills are higher than your income. You are mathematically underwater. The system cannot build wealth on a collapsing foundation. **You must immediately cancel subscriptions, negotiate bills, or take on extra income.** The system will not allow you to proceed until your Guilt-Free Margin is positive.")
        elif "leaving match money" in st.session_state.employer_match:
            st.warning("⚠️ **DIRECTIVE TRIGGERED: CAPTURE FREE MONEY**\n\nYour employer is offering you a guaranteed 100% return, and you are ignoring it. We do not invest or save extra cash until this is captured.")
            st.session_state.ack_match = st.checkbox("I commit to logging into my HR portal today to maximize my match.", value=st.session_state.ack_match)
            if st.session_state.ack_match:
                c2.button("Next: Assets & Debts", on_click=next_step, type="primary")
            else:
                c2.button("Acknowledge the directive above to continue", disabled=True)
        else:
            c2.button("Next: Assets & Debts", on_click=next_step, type="primary")
    else:
        c2.button("Fill in your numbers to continue", disabled=True)

# STAGE 2: ASSETS & DEBT GATES
elif st.session_state.step == 2:
    st.header("Step 2: Count your cash and list your debts.")
    st.caption("We check your cash against a 3-month survival target. Then, we analyze your debts to build a mathematically optimal payoff plan.")
    
    st.session_state.savings = st.number_input("Total Cash in Bank (Checking + Savings) ($)", min_value=0.0, step=500.0, value=st.session_state.savings, placeholder="e.g. 10000")

    st.divider()
    st.subheader("The Debt Ledger")
    
    # Added key="debt_editor_ui" to fix the double-typing focus glitch
    st.session_state.debt_df = st.data_editor(
        st.session_state.debt_df, 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True,
        key="debt_editor_ui"
    )
    
    st.divider()
    st.subheader("Debt Discovery Checklist")
    st.caption("To ensure the math is accurate, verify you have accounted for all potential liabilities. Check each box to confirm you have either listed the balance above, or verified you carry a zero balance for that category.")

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
    
    if st.session_state.savings is not None and all_checked:
        
        # Analyze for Toxic Debt
        has_toxic_debt = False
        if not st.session_state.debt_df.empty:
            temp_df = st.session_state.debt_df.copy()
            temp_df['APR (%)'] = pd.to_numeric(temp_df['APR (%)'], errors='coerce').fillna(0)
            toxic_df = temp_df[temp_df['APR (%)'] >= 7.0]
            if not toxic_df.empty:
                has_toxic_debt = True
        
        ef_target = com_val * 3
        
        # HARD STOP LOGIC
        if has_toxic_debt:
            st.error("🧨 **DIRECTIVE TRIGGERED: DESTROY TOXIC DEBT**\n\nYou are bleeding cash to high-interest debt (APR 7% or higher). You must route 100% of your Guilt-Free Margin directly to the principal of this debt until it is gone. Suspend all other saving goals.")
            st.session_state.ack_toxic = st.checkbox("I commit to avalanching my margin into this debt.", value=st.session_state.ack_toxic)
            if st.session_state.ack_toxic:
                c2.button("Next: Sinking Funds", on_click=next_step, type="primary")
            else:
                c2.button("Acknowledge the directive above to continue", disabled=True)
                
        elif st.session_state.savings < ef_target:
            st.warning(f"🛡️ **DIRECTIVE TRIGGERED: BUILD THE FORTRESS**\n\nYour debts are manageable, but your safety net is incomplete. Your survival target is \${ef_target:,.2f}. You must route 100% of your margin into a High-Yield Savings Account until this vault is full.")
            st.session_state.ack_ef = st.checkbox("I commit to prioritizing my safety net above all other goals.", value=st.session_state.ack_ef)
            if st.session_state.ack_ef:
                c2.button("Next: Sinking Funds", on_click=next_step, type="primary")
            else:
                c2.button("Acknowledge the directive above to continue", disabled=True)
        else:
            c2.button("Next: Sinking Funds", on_click=next_step, type="primary")
    else:
        c2.button("Complete reserves and the Debt Discovery Checklist to continue", disabled=True)

# STAGE 3: SINKING FUNDS
elif st.session_state.step == 3:
    st.header("Step 3: List your large, non-monthly bills.")
    st.caption("Predictable yearly expenses (like car registration or holidays) cause people to go into debt. By listing them here, we will slice them into small, automated monthly transfers so you are never surprised.")
    
    st.session_state.sinking_df = st.data_editor(
        st.session_state.sinking_df, 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True,
        key="sinking_editor_ui",
        column_config={
            "Frequency": st.column_config.SelectboxColumn("Frequency", options=["Annually", "Semi-Annually", "Quarterly"]),
            "Months Until Due": st.column_config.NumberColumn("Months Until Due", min_value=1, max_value=12)
        }
    )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: The Moat", on_click=next_step, type="primary")

# STAGE 4: THE MOAT
elif st.session_state.step == 4:
    st.header("Step 4: Protect your dependents.")
    st.caption("If people rely on your income to survive, you need a protective moat. We only recommend pure Term Life insurance because it is cheap, effective, and mathematically superior to whole life policies.")
    
    st.session_state.has_dependents = st.radio(
        "Does anyone rely on your income to sustain their basic standard of living?", 
        ["No", "Yes, I have dependents"]
    )
    
    if st.session_state.has_dependents == "Yes, I have dependents":
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.income_gap = st.number_input(
                "Annual income required to support dependents if you pass ($):", 
                min_value=0.0, step=5000.0, value=st.session_state.income_gap, placeholder="e.g. 50000"
            )
        with col2:
            st.session_state.term_years = st.number_input(
                "Years until dependents reach financial self-sufficiency:", 
                min_value=1, max_value=40, value=st.session_state.term_years
            )
            
        if st.session_state.income_gap is not None and st.session_state.income_gap > 0:
            coverage = st.session_state.income_gap * 25
            st.success(f"🛡️ **Moat Specification:** Secure a **{st.session_state.term_years}-year level Term Life policy** for **\${coverage:,.2f}**.")
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: Goal Trajectory", on_click=next_step, type="primary")

# STAGE 5: GOAL TRAJECTORY (WITH COMPOUND INTEREST)
elif st.session_state.step == 5:
    st.header("Step 5: Set a specific financial goal.")
    st.caption("Setting a goal requires serious thought. Money without direction is easily wasted. What are you actually buying back your time for? Examples of common, high-impact goals: A 20% down payment on a house, a 6-month 'F-You' opportunity fund, paying cash for a reliable car, or maxing out a Roth IRA for the year.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.goal_name = st.text_input("Target Win / Objective", value=st.session_state.goal_name, placeholder="e.g. House Down Payment")
    with col2:
        st.session_state.goal_target = st.number_input("Target Capital Required ($)", min_value=0.0, step=1000.0, value=st.session_state.goal_target, placeholder="e.g. 40000")
    
    if margin > 0 and st.session_state.goal_target and st.session_state.goal_name:
        # Compound Interest Math (Assuming 7% annual return)
        annual_rate = 0.07
        monthly_rate = annual_rate / 12
        
        try:
            # Formula to find 'n' months for Future Value of a series
            n_months = math.ceil(math.log((st.session_state.goal_target * monthly_rate / margin) + 1) / math.log(1 + monthly_rate))
        except:
            n_months = int(st.session_state.goal_target // margin) + 1
            
        years = n_months // 12
        rem_months = n_months % 12
        time_str = f"{years} yr, {rem_months} mo" if years > 0 else f"{rem_months} months"
        
        st.success(f"🎯 **Trajectory Locked:** By investing your **\${margin:,.2f}** monthly margin at an estimated 7% annualized return, you will achieve **\${st.session_state.goal_target:,.2f}** for '{st.session_state.goal_name}' in **{time_str}**.")
        
        # Build strict calendar dates to prevent chart dipping
        timeline_data = []
        current_date = datetime.date.today()
        accumulated = 0
        
        for m in range(n_months + 1):
            if m > 0:
                accumulated = (accumulated + margin) * (1 + monthly_rate)
            
            display_val = min(accumulated, st.session_state.goal_target)
            target_date = current_date + pd.DateOffset(months=m)
            timeline_data.append({"Date": target_date, "Capital ($)": display_val})
            
        df_chart = pd.DataFrame(timeline_data).set_index("Date")
        st.line_chart(df_chart)
        
    elif margin <= 0:
        st.error("No positive Guilt-Free Margin available to model. Fixed expenses and debt minimums must be restructured first.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: Complete Audit", on_click=next_step, type="primary")

# STAGE 6: FINAL CHECKOUT
elif st.session_state.step == 6:
    st.header("Step 6: System Armed")
    st.caption("You have successfully audited your baseline and mathematically mapped your path. Stick to the commitments you checked off during this process.")
    
    st.success("✅ **AUDIT COMPLETE.** Check your Snapshot on the left to verify your final Guilt-Free Margin.")
    
    st.divider()
    st.subheader("System Governance & Failsafes")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.error("🚫 **Prohibited Speculation:** Margin leverage, options contracts, market timing, and whole life insurance policies are disallowed by this protocol.")
    with col_g2:
        st.info("🏛️ **Fiduciary Threshold:** Upon maximizing all statutory tax-advantaged limits ($23.5k 401k, $7k IRA) and accumulating complex taxable estate requirements, hand off management to a fee-only Registered Investment Advisor (RIA).")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("🔄 Restart Audit", on_click=reset)
