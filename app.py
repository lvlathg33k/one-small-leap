import streamlit as st
import pandas as pd
import datetime
import math

st.set_page_config(page_title="One Small Leap", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 0
if 'household' not in st.session_state: st.session_state.household = "Single Operator"
if 'take_home' not in st.session_state: st.session_state.take_home = None
if 'base_committed' not in st.session_state: st.session_state.base_committed = None
if 'employer_match' not in st.session_state: st.session_state.employer_match = "Select..."
if 'savings' not in st.session_state: st.session_state.savings = None
if 'investments' not in st.session_state: st.session_state.investments = None
if 'debts' not in st.session_state: st.session_state.debts = []
if 'sinking_funds' not in st.session_state: st.session_state.sinking_funds = []
if 'goal_name' not in st.session_state: st.session_state.goal_name = ""
if 'goal_target' not in st.session_state: st.session_state.goal_target = None
if 'has_hsa' not in st.session_state: st.session_state.has_hsa = "No"

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1
def reset(): 
    for key in st.session_state.keys():
        del st.session_state[key]

# ==========================================
# MATH & SNAPSHOT ENGINE
# ==========================================
th_val = st.session_state.take_home or 0.0
base_com_val = st.session_state.base_committed or 0.0

# Calculate Sinking Fund Impact
sinking_monthly = 0.0
for sf in st.session_state.sinking_funds:
    freq_div = {"Annually": 12, "Semi-Annually": 6, "Quarterly": 3}
    sinking_monthly += sf['Cost'] / freq_div[sf['Frequency']]

# Total Committed = Base + Sinking
com_val = base_com_val + sinking_monthly
margin = th_val - com_val

with st.sidebar:
    st.header("Your Snapshot")
    st.markdown(f"**Total Take-Home**<br><span style='color: #4da6ff; font-size: 24px; font-weight: bold;'>\${th_val:,.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Committed Money**<br><span style='color: #cc0000; font-size: 24px; font-weight: bold;'>\${com_val:,.2f}</span>", unsafe_allow_html=True)
    if sinking_monthly > 0:
        st.caption(f"(Includes \${sinking_monthly:,.2f} automated sinking funds)")
    
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

if st.session_state.step == 0:
    st.title("One Small Leap")
    st.caption("This system mathematically prioritizes your capital. It does not give suggestions; it issues operational directives. If your inputs indicate a critical failure, the system will lock down and instruct you to fix the reality of your finances before allowing you to model wealth generation.")
    st.session_state.household = st.radio("Household Architecture:", ["Single Operator", "Married (Joint Finances)"])
    st.button("Begin", on_click=next_step, type="primary")

elif st.session_state.step == 1:
    st.header("Step 1: Cash Flow Baseline")
    st.caption("We need to know your operational baseline. **DO NOT include large, multi-month expenses here** (like annual car registration or Christmas). We will factor those in later. Only include strict monthly minimums.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.take_home = st.number_input("Monthly Net Take-Home Pay ($)", min_value=0.0, step=100.0, value=st.session_state.take_home)
        st.markdown("### ")
        st.session_state.employer_match = st.radio(
            "Are you currently capturing 100% of your employer's 401(k) match?", 
            ["Select...", "Yes / My employer offers no match", "No, I am leaving match money on the table"]
        )
    with col2:
        st.session_state.base_committed = st.number_input("Monthly Baseline Committed Bills ($)", min_value=0.0, step=100.0, value=st.session_state.base_committed)
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.take_home is not None and st.session_state.base_committed is not None and st.session_state.employer_match != "Select...":
        if margin <= 0:
            st.error("🚨 **Your One Next Step: Stop the Bleeding**\n\nYour basic bills exceed or equal your income. You are mathematically underwater.\n\n**Action Required:** Leave this app. Cancel subscriptions, negotiate bills, or take on extra income. You cannot proceed until you change the 'Committed Bills' input above to generate a positive margin.")
        elif "leaving match money" in st.session_state.employer_match:
            st.warning("⚠️ **Your One Next Step: Capture Free Money**\n\nYour employer is offering you a guaranteed 100% return, and you are actively ignoring it.\n\n**Action Required:** Leave this app. Log into your HR portal and increase your contribution to the exact match limit. Once completed, change the radio button above to unlock the system.")
        else:
            c2.button("Next: Count Your Cash", on_click=next_step, type="primary")
    else:
        c2.button("Fill in your numbers to continue", disabled=True)

elif st.session_state.step == 2:
    st.header("Step 2: Liquid Assets & Reallocation")
    st.caption("Input everything sitting in your checking and savings accounts, followed by any liquid investments (taxable brokerage accounts). Do not include retirement accounts here.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.savings = st.number_input("Total Cash in Bank ($)", min_value=0.0, step=500.0, value=st.session_state.savings)
    with col2:
        st.session_state.investments = st.number_input("Liquid Taxable Investments ($)", min_value=0.0, step=500.0, value=st.session_state.investments)
        
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.savings is not None and st.session_state.investments is not None:
        ef_target = com_val * 3
        surplus_cash = st.session_state.savings - ef_target
        
        if st.session_state.savings < ef_target and st.session_state.investments > 0:
             st.warning(f"⚠️ **Reallocation Directive:** Your cash safety net is underfunded by \${(ef_target - st.session_state.savings):,.2f}, but you have \${st.session_state.investments:,.2f} exposed in the market. Consider liquidating taxable investments to fill your cash moat to \${ef_target:,.2f}.")
             c2.button("Acknowledge & Proceed", on_click=next_step, type="primary")
        elif surplus_cash > 0:
             st.info(f"💡 **Reallocation Directive:** Your cash safety net is full, and you have **\${surplus_cash:,.2f}** in surplus cash losing value to inflation. Be prepared to deploy this surplus against debt in the next step.")
             c2.button("Next: The Debt Ledger", on_click=next_step, type="primary")
        elif st.session_state.savings < ef_target:
             st.error(f"🛡️ **Your One Next Step: Build the Fortress**\n\nYour 3-month survival target is \${ef_target:,.2f}. You must route 100% of your margin into a High-Yield Savings Account until this vault is full.\n\n**Action Required:** Leave this app. Automate a \${margin:,.2f} monthly transfer to your savings. You cannot proceed to wealth planning until you change your 'Total Cash' input above to meet your target.")
        else:
             c2.button("Next: The Debt Ledger", on_click=next_step, type="primary")
    else:
        c2.button("Fill in your numbers to continue", disabled=True)

elif st.session_state.step == 3:
    st.header("Step 3: The Debt Ledger")
    st.caption("List every liability. The system will apply the Avalanche Method to map your exact payoff timeline.")
    
    with st.form("add_debt_form", clear_on_submit=True):
        st.write("Add a Liability")
        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        d_name = d_c1.text_input("Name (e.g. Chase Visa)")
        d_bal = d_c2.number_input("Balance ($)", min_value=0.0)
        d_apr = d_c3.number_input("APR (%)", min_value=0.0)
        d_min = d_c4.number_input("Min Payment ($)", min_value=0.0)
        submitted = st.form_submit_button("Add to Ledger")
        if submitted and d_name and d_bal > 0:
            st.session_state.debts.append({"Name": d_name, "Balance": d_bal, "APR": d_apr, "Min": d_min})
            st.rerun()

    if st.session_state.debts:
        df_debts = pd.DataFrame(st.session_state.debts)
        st.dataframe(df_debts, use_container_width=True, hide_index=True)
        if st.button("Clear Ledger"):
            st.session_state.debts = []
            st.rerun()

        # Avalanche Math
        temp_debts = [{'Name': d['Name'], 'Bal': d['Balance'], 'APR': d['APR'], 'Min': d['Min']} for d in st.session_state.debts]
        temp_debts.sort(key=lambda x: x['APR'], reverse=True)
        
        timeline_results = []
        sim_months = 0
        active_margin = margin
        
        while sum(d['Bal'] for d in temp_debts) > 0 and sim_months < 600:
            sim_months += 1
            freed_up = 0
            
            # Apply minimums & interest
            for d in temp_debts:
                if d['Bal'] > 0:
                    interest = d['Bal'] * (d['APR'] / 100 / 12)
                    d['Bal'] += interest
                    payment = min(d['Min'], d['Bal'])
                    d['Bal'] -= payment
                    if d['Bal'] <= 0.01:
                        d['Bal'] = 0
                        timeline_results.append({"Debt": d['Name'], "Months to Zero": sim_months})
                        freed_up += d['Min']
                else:
                    freed_up += d['Min']
            
            # Apply margin + freed up minimums to highest APR
            extra_cash = active_margin + freed_up
            for d in temp_debts:
                if d['Bal'] > 0:
                    payment = min(extra_cash, d['Bal'])
                    d['Bal'] -= payment
                    extra_cash -= payment
                    if d['Bal'] <= 0.01:
                        d['Bal'] = 0
                        timeline_results.append({"Debt": d['Name'], "Months to Zero": sim_months})
                    if extra_cash <= 0:
                        break

        if timeline_results:
            st.markdown("### Avalanche Timeline")
            st.caption(f"Based on routing your full \${margin:,.2f} margin plus all minimum payments toward the highest APR.")
            tl_df = pd.DataFrame(timeline_results)
            tl_df['Payoff Date'] = [datetime.date.today() + pd.DateOffset(months=m) for m in tl_df['Months to Zero']]
            tl_df['Payoff Date'] = tl_df['Payoff Date'].dt.strftime('%B %Y')
            st.dataframe(tl_df[['Debt', 'Payoff Date']], use_container_width=True, hide_index=True)
            
            has_toxic = any(d['APR'] >= 7.0 for d in st.session_state.debts)
            if has_toxic:
                st.error("🧨 **Your One Next Step: Destroy High-Interest Debt**\n\nYou have toxic debt holding you back. You must route 100% of your Guilt-Free Margin directly to the principal of your highest APR debt.\n\n**Action Required:** Leave this app. Set up an automatic transfer. You cannot proceed to wealth planning until you change this ledger to reflect $0 balances for all debt over 7% APR.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.debts and any(d['APR'] >= 7.0 for d in st.session_state.debts):
        c2.button("Clear Toxic Debt to Proceed", disabled=True)
    else:
        c2.button("Next: Sinking Funds", on_click=next_step, type="primary")

elif st.session_state.step == 4:
    st.header("Step 4: Sinking Funds")
    st.caption("List your predictable non-monthly expenses (Car Registration, Christmas, Vacations). Adding these will actively reduce your Guilt-Free Margin on the left sidebar to ensure you are actually saving for them.")
    
    with st.form("add_sinking_form", clear_on_submit=True):
        sc1, sc2, sc3 = st.columns(3)
        s_name = sc1.text_input("Expense Name")
        s_cost = sc2.number_input("Total Cost ($)", min_value=0.0)
        s_freq = sc3.selectbox("Frequency", ["Annually", "Semi-Annually", "Quarterly"])
        s_sub = st.form_submit_button("Add Sinking Fund")
        if s_sub and s_name and s_cost > 0:
            st.session_state.sinking_funds.append({"Expense Name": s_name, "Cost": s_cost, "Frequency": s_freq})
            st.rerun()

    if st.session_state.sinking_funds:
        st.dataframe(pd.DataFrame(st.session_state.sinking_funds), use_container_width=True, hide_index=True)
        if st.button("Clear Funds"):
            st.session_state.sinking_funds = []
            st.rerun()

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.sinking_funds:
        st.info("📅 **Your One Next Step: Automate Sinking Funds**\n\nLog into your bank, open separate checking folders, and set up automated monthly transfers for the bills listed above so they stop surprising you.")
    
    c2.button("Next: The Wealth Engine", on_click=next_step, type="primary")

elif st.session_state.step == 5:
    st.header("Step 5: The Wealth Engine")
    st.caption("You have survived the gauntlet. You have zero toxic debt, a fully funded safety net, and automated sinking funds. It is time to deploy your unallocated margin into wealth generation.")
    
    st.session_state.has_hsa = st.radio("Are you enrolled in a High-Deductible Health Plan (HDHP)?", ["No", "Yes"])
    
    st.markdown("### The Capital Allocation Waterfall")
    st.markdown("""
    Do not skip steps. Max out the limit on one tier before deploying capital to the next.
    1. **401(k) Match:** (Already captured in Step 1)
    """)
    if st.session_state.has_hsa == "Yes":
        st.markdown("2. **Health Savings Account (HSA):** Max this out. It is triple-tax-advantaged. Do not spend it on medical bills; invest it in broad-market funds and pay cash for medical expenses.")
        st.markdown("3. **Roth IRA:** Max out statutory limits ($7,000/yr). Invest in low-cost factor-tilt index funds (e.g., small-cap value).")
        st.markdown("4. **Max 401(k):** Return to your employer plan and fill it to the $23,500 maximum.")
        st.markdown("5. **Taxable Brokerage:** Deploy all remaining margin into standard brokerage ETFs.")
    else:
        st.markdown("2. **Roth IRA:** Max out statutory limits ($7,000/yr). Invest in low-cost factor-tilt index funds (e.g., small-cap value).")
        st.markdown("3. **Max 401(k):** Return to your employer plan and fill it to the $23,500 maximum.")
        st.markdown("4. **Taxable Brokerage:** Deploy all remaining margin into standard brokerage ETFs.")

    st.divider()
    st.subheader("Goal Trajectory Modeling")
    st.caption("Assume a conservative 7% real annualized return.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.goal_name = st.text_input("Target Objective", value=st.session_state.goal_name, placeholder="e.g. Early Retirement Milestone")
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

