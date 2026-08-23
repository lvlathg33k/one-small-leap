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
    st.metric("Total Take-Home", f"${th_val:,.2f}")
    st.metric("Committed Money", f"${com_val:,.2f}")
    st.metric("Guilt-Free Margin", f"${margin:,.2f}", 
              delta=f"${margin:,.2f}" if margin > 0 else f"-${abs(margin):,.2f}", 
              delta_color="normal" if margin > 0 else "inverse")
    
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
    st.markdown("""
    Most financial platforms shame you for small daily expenses without providing a structured system. 
    
    This application audits your baseline, sequences debt and reserves through mathematical prioritization, protects your dependents, and outputs your **single next operational action**.
    """)
    st.session_state.household = st.radio("Household Architecture:", ["Single", "Married (Joint Finances)"])
    st.button("Begin Audit", on_click=next_step, type="primary")

# STAGE 1: CASH FLOW
elif st.session_state.step == 1:
    st.header("Step 1: Cash Flow Baseline")
    st.markdown("Quantify total net liquidity entering and strictly committed to leave each month.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Money In:** Find 'Net Pay' on your most recent paystub (take-home cash post-tax). Scale to a monthly figure.")
        st.session_state.take_home = st.number_input("Monthly Net Take-Home Pay ($)", min_value=0.0, step=100.0, value=st.session_state.take_home, placeholder="e.g. 5000")
        
        st.markdown("### ")
        st.session_state.employer_match = st.radio(
            "Does your employer offer a 401(k) / retirement match you are NOT currently capturing?", 
            ["No / I already get the full match", "Yes, I am leaving match money on the table"]
        )

    with col2:
        st.info("💡 **Money Out:** Sum all non-negotiable monthly obligations (rent/mortgage, utilities, essential groceries, minimum debt payments).")
        st.session_state.committed = st.number_input("Monthly Baseline Committed Bills ($)", min_value=0.0, step=100.0, value=st.session_state.committed, placeholder="e.g. 3500")
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.take_home is not None and st.session_state.committed is not None:
        c2.button("Next: Assets & Debts", on_click=next_step, type="primary")
    else:
        c2.button("Complete cash flow inputs to continue", disabled=True)

# STAGE 2: ASSETS & LIABILITIES
elif st.session_state.step == 2:
    st.header("Step 2: Assets & Liabilities")
    
    st.subheader("Core Reserves")
    st.markdown(f"Your calculated monthly operating baseline is **${st.session_state.committed:,.2f}**. A standard 3-month liquidity target requires **${(st.session_state.committed * 3):,.2f}**.")
    st.session_state.savings = st.number_input("Current Liquid Cash (Checking + Savings Accounts) ($)", min_value=0.0, step=500.0, value=st.session_state.savings, placeholder="e.g. 10000")

    st.divider()
    st.subheader("Debt Ledger")
    st.markdown("Enter all active liabilities. The triage engine automatically segments toxic interest rates (>= 7% APR).")
    
    st.session_state.debt_df = st.data_editor(st.session_state.debt_df, num_rows="dynamic", use_container_width=True)
    
    st.markdown("### ")
    st.session_state.debt_confirm = st.radio("Debt Attestation:", 
                                             ["Select...", "I have zero active debt.", "I confirm this ledger contains ALL active liabilities."])

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.savings is not None and st.session_state.debt_confirm != "Select...":
        c2.button("Next: Sinking Funds", on_click=next_step, type="primary")
    else:
        c2.button("Complete reserves and debt attestation to continue", disabled=True)

# STAGE 3: SINKING FUNDS
elif st.session_state.step == 3:
    st.header("Step 3: Sinking Funds (Smoothing Spikes)")
    st.markdown("""
    Non-monthly predictable liabilities (annual insurance premiums, vehicle registration, holiday reserves) disrupt cash flow when treated as ad-hoc expenses. 
    
    Sinking funds amortize these obligations into fixed monthly reserve transfers to maintain baseline stability.
    """)
    
    st.session_state.sinking_df = st.data_editor(
        st.session_state.sinking_df, 
        num_rows="dynamic", 
        use_container_width=True,
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
    st.header("Step 4: The Moat (Pure Protection)")
    st.markdown("Insurance is purely a tool for capital replacement, not wealth accumulation. Cash-value and whole life instruments are mathematically inefficient.")
    
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
            st.success(f"🛡️ **Moat Specification:** Secure a **{st.session_state.term_years}-year level Term Life policy** for **${coverage:,.2f}**.")
            st.caption("Calculation based on a 4% capitalization rate (25x annual replacement requirement).")
    
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
    s("Step 5: Wealth Engine & Goal Trajectory")
    st.markdown("Model specific capital milestones against your active monthly Guilt-Free Margin.")
    
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
        
        st.success(f"🎯 **Trajectory Locked:** Routing your **${margin:,.2f}** monthly margin achieves **${st.session_state.goal_target:,.2f}** for '{st.session_state.goal_name}' in **{time_str}**.")
        
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
    st.header("Step 6: The Prime Directive")
    st.markdown("Based on systemic mathematical triage, execute your **single immediate priority** before deploying capital elsewhere.")
    
    # Process Liabilities
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
    
    # 1. Negative Margin Check
    if margin <= 0:
        st.error("🚨 **PRIORITY 1: LIQUIDITY STRESS RECOVERY**")
        st.markdown(f"Committed bills (${com_val:,.2f}) exceed or match take-home pay (${th_val:,.2f}). Immediate action: eliminate discretionary fixed costs or increase gross cash flow until net margin is positive.")
    
    # 2. Employer Match Capture
    elif "leaving match money" in st.session_state.employer_match:
        st.warning("⚠️ **PRIORITY 2: CAPTURE 100% EMPLOYER MATCH**")
        st.markdown("Employer match represents an instantaneous, risk-free guaranteed return. Update your workplace retirement contribution percentage to the maximum matched ceiling immediately.")
    
    # 3. Toxic Debt Avalanche
    elif has_toxic_debt:
        highest_rate = toxic_df.iloc[0]
        st.error("🧨 **PRIORITY 3: AVALANCHE HIGH-INTEREST DEBT (>= 7% APR)**")
        st.markdown(f"Deploy 100% of your **${margin:,.2f}** monthly margin to principal reduction on **{highest_rate['Debt Name']}** ({highest_rate['APR (%)']}% APR). Suspend additional investments and cash accumulation.")
        st.dataframe(toxic_df[["Debt Name", "Balance ($)", "APR (%)"]], use_container_width=True)
        
    # 4. Emergency Vault Calibration
    elif current_savings < ef_target:
        deficit = ef_target - current_savings
        st.warning("🛡️ **PRIORITY 4: CAPITALIZE CORE 3-MONTH RESERVE**")
        st.markdown(f"Your target liquidity is **${ef_target:,.2f}** (Current: ${current_savings:,.2f}). Route your **${margin:,.2f}** monthly margin to a dedicated High-Yield Savings Account until the **${deficit:,.2f}** deficit is closed.")
        
    # 5. Sinking Fund Activation
    elif not st.session_state.sinking_df.empty:
        st.info("📅 **PRIORITY 5: AUTOMATE SINKING RESERVES**")
        st.markdown("Baseline liquid security established. Establish automated recurring transfers for identified periodic liabilities to prevent baseline drawdowns.")
        st.dataframe(st.session_state.sinking_df, use_container_width=True)
        
    # 6. Unconstrained Factor Indexing
    else:
        st.success("📈 **PRIORITY 6: LONG-TERM CAPITAL COMPOUNDING**")
        st.markdown(f"Fortress baseline complete. Deploy your unallocated **${margin:,.2f}** monthly margin into low-cost, broad-market equity index funds (e.g., small-cap value factor tilts) across tax-advantaged accounts (Roth IRA / HSA / 401k) and taxable brokerage.")

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
