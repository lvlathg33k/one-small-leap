import streamlit as st
import pandas as pd
import datetime

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
if 'debt_confirm' not in st.session_state: st.session_state.debt_confirm = "Select..."
if 'sinking_df' not in st.session_state: 
    st.session_state.sinking_df = pd.DataFrame(columns=["Expense Name", "Total Cost ($)", "Frequency", "Months Until Due"])
if 'has_dependents' not in st.session_state: st.session_state.has_dependents = "No"
if 'income_gap' not in st.session_state: st.session_state.income_gap = None
if 'term_years' not in st.session_state: st.session_state.term_years = 20
if 'goal_name' not in st.session_state: st.session_state.goal_name = ""
if 'goal_target' not in st.session_state: st.session_state.goal_target = None
if 'debt_strategy' not in st.session_state: st.session_state.debt_strategy = "Combine & Conquer"

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1
def reset(): 
    st.session_state.step = 0
    st.session_state.take_home = None
    st.session_state.committed = None
    st.session_state.savings = None
    st.session_state.debt_confirm = "Select..."
    st.session_state.goal_name = ""
    st.session_state.goal_target = None

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

# STAGE 1: CASH FLOW
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
    
    if st.session_state.take_home is not None and st.session_state.committed is not None:
        c2.button("Next: Assets & Debts", on_click=next_step, type="primary")
    else:
        c2.button("Fill in your numbers to continue", disabled=True)

# STAGE 2: ASSETS & LIABILITIES
elif st.session_state.step == 2:
    st.header("Step 2: Count your cash and list your debts.")
    st.caption("If you lost your job today, you need cash to survive. We check your cash against a 3-month survival target. Then, we analyze your debts to build a mathematically optimal payoff plan.")
    
    st.session_state.savings = st.number_input("Total Cash in Bank (Checking + Savings) ($)", min_value=0.0, step=500.0, value=st.session_state.savings, placeholder="e.g. 10000")

    st.divider()
    st.subheader("The Debt Ledger")
    
    st.session_state.debt_df = st.data_editor(
        st.session_state.debt_df, 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("### ")
    st.session_state.debt_confirm = st.radio("Debt Attestation:", 
                                             ["Select...", "I have zero active debt.", "I confirm this ledger contains ALL my active debts."])

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.savings is not None and st.session_state.debt_confirm != "Select...":
        c2.button("Next: Sinking Funds", on_click=next_step, type="primary")
    else:
        c2.button("Complete reserves and debt attestation to continue", disabled=True)

# STAGE 3: SINKING FUNDS
elif st.session_state.step == 3:
    st.header("Step 3: List your large, non-monthly bills.")
    st.caption("Predictable yearly expenses (like car registration or holidays) cause people to go into debt. By listing them here, we will slice them into small, automated monthly transfers so you are never surprised.")
    
    st.session_state.sinking_df = st.data_editor(
        st.session_state.sinking_df, 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Frequency": st.column_config.SelectboxColumn("Frequency", options=["Annually", "Semi-Annually", "Quarterly"]),
            "Months Until Due": st.column_config.NumberColumn("Months Until Due", min_value=1, max_value=12)
        }
    )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: The Moat", on_click=next_step, type="primary")

# STAGE 4: THE MOAT (RISK MANAGEMENT)
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
    
    if "Married" in st.session_state.household:
        st.divider()
        st.subheader("Joint Debt Governance")
        st.session_state.debt_strategy = st.radio(
            "Pre-marital liability strategy:",
            ["Combine & Conquer (Pool all liabilities into household margin)", 
             "Individual Autonomy (Isolate prior liabilities to the originating individual)"]
        )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: Goal Trajectory", on_click=next_step, type="primary")

# STAGE 5: GOAL TRAJECTORY
elif st.session_state.step == 5:
    st.header("Step 5: Set a specific financial goal.")
    st.caption("Money is a tool to buy back your freedom. Tell the system what you are saving for, and it will map out your exact timeline.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.goal_name = st.text_input("Target Win / Objective", value=st.session_state.goal_name, placeholder="e.g. Down Payment, Opportunity Fund")
    with col2:
        st.session_state.goal_target = st.number_input("Target Capital Required ($)", min_value=0.0, step=1000.0, value=st.session_state.goal_target, placeholder="e.g. 30000")
    
    if margin > 0 and st.session_state.goal_target and st.session_state.goal_name:
        months_needed = int(st.session_state.goal_target // margin) + (1 if st.session_state.goal_target % margin != 0 else 0)
        years = months_needed // 12
        rem_months = months_needed % 12
        time_str = f"{years} yr, {rem_months} mo" if years > 0 else f"{rem_months} months"
        
        st.success(f"🎯 **Trajectory Locked:** Routing your **\${margin:,.2f}** monthly margin achieves **\${st.session_state.goal_target:,.2f}** for '{st.session_state.goal_name}' in **{time_str}**.")
        
        timeline_data = [
            {"Month": f"M{m}", "Accumulated Capital ($)": min(m * margin, st.session_state.goal_target)} 
            for m in range(months_needed + 1)
        ]
        st.line_chart(pd.DataFrame(timeline_data).set_index("Month"))
    elif margin <= 0:
        st.error("No positive Guilt-Free Margin available to model. Fixed expenses and debt minimums must be restructured first.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next: Prime Directive", on_click=next_step, type="primary")

# STAGE 6: THE PRIME DIRECTIVE (EXECUTION WATERFALL)
elif st.session_state.step == 6:
    st.header("Step 6: Your Action Plan")
    st.caption("Do not look at step 2 until step 1 is done. Execute this single priority right now.")
    
    has_toxic_debt = False
    toxic_df = pd.DataFrame()
    if not st.session_state.debt_df.empty:
        st.session_state.debt_df['APR (%)'] = pd.to_numeric(st.session_state.debt_df['APR (%)'], errors='coerce').fillna(0)
        st.session_state.debt_df['Balance ($)'] = pd.to_numeric(st.session_state.debt_df['Balance ($)'], errors='coerce').fillna(0)
        toxic_df = st.session_state.debt_df[st.session_state.debt_df['APR (%)'] >= 7.0].sort_values(by='APR (%)', ascending=False)
        if not toxic_df.empty:
            has_toxic_debt = True
            
    ef_target = (st.session_state.committed or 0.0) * 3
    current_savings = st.session_state.savings or 0.0
    
    # 1. Negative Margin
    if margin <= 0:
        st.error("🚨 STOP THE BLEEDING")
        st.markdown(f"Your bills (\${com_val:,.2f}) are higher than your income (\${th_val:,.2f}). You must cancel subscriptions, negotiate bills, or increase your income immediately until your margin is green.")
    
    # 2. Employer Match
    elif "leaving match money" in st.session_state.employer_match:
        st.warning("⚠️ CAPTURE FREE MONEY")
        st.markdown("Your employer is offering a guaranteed return. Log into your HR portal today and increase your 401(k) contribution to the full match limit.")
    
    # 3. Toxic Debt
    elif has_toxic_debt:
        highest_rate = toxic_df.iloc[0]
        st.error("🧨 DESTROY HIGH-INTEREST DEBT")
        st.markdown(f"You are bleeding cash to high-interest debt. Route 100% of your **\${margin:,.2f}** margin directly to the principal of **{highest_rate['Debt Name']}** ({highest_rate['APR (%)']}% APR) until it is gone. Suspend all other saving.")
        st.dataframe(toxic_df[["Debt Name", "Balance ($)", "APR (%)"]], use_container_width=True, hide_index=True)
        
    # 4. Emergency Vault
    elif current_savings < ef_target:
        st.warning("🛡️ BUILD THE FORTRESS")
        st.markdown(f"Your debts are manageable, but your safety net is incomplete. Your target is **\${ef_target:,.2f}** and you have **\${current_savings:,.2f}**. Route 100% of your **\${margin:,.2f}** margin into a High-Yield Savings Account every month until you hit your target.")
        
    # 5. Sinking Funds
    elif not st.session_state.sinking_df.empty:
        st.info("📅 AUTOMATE SINKING FUNDS")
        st.markdown("Your safety net is full and toxic debt is gone. Log into your bank, open sub-folders (or a separate checking account), and set up automated monthly transfers for the bills listed below.")
        st.dataframe(st.session_state.sinking_df, use_container_width=True, hide_index=True)
        
    # 6. Wealth Generation
    else:
        st.success("📈 COMPOUND YOUR WEALTH")
        st.markdown(f"Fortress baseline complete. Deploy your unallocated **\${margin:,.2f}** monthly margin into low-cost, broad-market equity index funds (e.g., small-cap value factor tilts) to build long-term wealth.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("🔄 Restart Audit", on_click=reset)
