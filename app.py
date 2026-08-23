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

# Cash Flow
if 'take_home' not in st.session_state: st.session_state.take_home = None
if 'base_committed' not in st.session_state: st.session_state.base_committed = None
if 'employer_match' not in st.session_state: st.session_state.employer_match = "Select..."

# Assets
if 'ast_checking' not in st.session_state: st.session_state.ast_checking = None
if 'ast_savings' not in st.session_state: st.session_state.ast_savings = None
if 'ast_trad_ira' not in st.session_state: st.session_state.ast_trad_ira = None
if 'ast_roth_ira' not in st.session_state: st.session_state.ast_roth_ira = None
if 'ast_taxable' not in st.session_state: st.session_state.ast_taxable = None
if 'ast_hsa' not in st.session_state: st.session_state.ast_hsa = None
if 'ast_home' not in st.session_state: st.session_state.ast_home = None

# Debts & Sinking Funds
if 'debt_df' not in st.session_state: 
    st.session_state.debt_df = pd.DataFrame(columns=["Debt Name", "Balance ($)", "APR (%)", "Min Payment ($)"])
if 'sinking_df' not in st.session_state: 
    st.session_state.sinking_df = pd.DataFrame(columns=["Expense Name", "Total Cost ($)", "Frequency", "Months Until Due"])

# Checkboxes
if 'cc_check' not in st.session_state: st.session_state.cc_check = False
if 'auto_check' not in st.session_state: st.session_state.auto_check = False
if 'student_check' not in st.session_state: st.session_state.student_check = False
if 'mortgage_check' not in st.session_state: st.session_state.mortgage_check = False
if 'payday_check' not in st.session_state: st.session_state.payday_check = False

# HSA & Goals
if 'hdhp_status' not in st.session_state: st.session_state.hdhp_status = "Select..."
if 'goal_name' not in st.session_state: st.session_state.goal_name = ""
if 'goal_target' not in st.session_state: st.session_state.goal_target = None

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

sinking_monthly = 0.0
if not st.session_state.sinking_df.empty:
    for index, row in st.session_state.sinking_df.iterrows():
        freq_div = {"Annually": 12, "Semi-Annually": 6, "Quarterly": 3}
        sinking_monthly += row['Total Cost ($)'] / freq_div.get(row['Frequency'], 12)

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
    total_steps = 11
    st.progress(min((st.session_state.step) / total_steps, 1.0))
    st.caption(f"Stage {st.session_state.step} of {total_steps}")

# ==========================================
# MAIN UI: THE WIZARD FLOW
# ==========================================

# STAGE 0: SETUP
if st.session_state.step == 0:
    st.title("One Small Leap")
    st.caption("This system mathematically prioritizes your capital. It does not give suggestions; it issues operational directives. We take action to overcome overthinking.")
    st.session_state.household = st.radio("Household Architecture:", ["Single Operator", "Married (Joint Finances)"])
    st.button("Begin", on_click=next_step, type="primary")

# STAGE 1: INCOME
elif st.session_state.step == 1:
    st.header("Step 1: Cash Flow")
    st.caption("Let's establish your baseline. We need to know exactly how much cash hits your bank account every month.")
    st.session_state.take_home = st.number_input("Monthly Net Take-Home Pay ($)", min_value=0.0, step=100.0, value=st.session_state.take_home, help="Look at your paystub. Find the 'Net Pay' (what actually lands in your checking account after taxes and deductions). Scale that to a monthly number.")
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    if st.session_state.take_home is not None and st.session_state.take_home > 0:
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Enter your income to continue", disabled=True)

# STAGE 2: THE 401K GATE
elif st.session_state.step == 2:
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

# STAGE 3: BASELINE EXPENSES
elif st.session_state.step == 3:
    st.header("Step 3: Baseline Expenses")
    st.caption("What absolutely must leave your account every month to keep the lights on? **DO NOT include large, multi-month expenses here** (like annual car registration or Christmas). We will factor those in later. Only include strict monthly minimums (rent, groceries, utilities, minimum debt payments).")
    
    st.session_state.base_committed = st.number_input("Monthly Baseline Committed Bills ($)", min_value=0.0, step=100.0, value=st.session_state.base_committed)
    
    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if st.session_state.base_committed is not None:
        if margin <= 0:
            st.error("🚨 **Your One Next Step: Stop the Bleeding**\n\nYour basic bills exceed or equal your income. You are mathematically underwater.\n\n**Action Required:** Leave this app right now. Cancel subscriptions, negotiate bills, or take on extra income. You cannot proceed until you change the 'Committed Bills' input above to generate a positive margin.")
        else:
            c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Enter your expenses to continue", disabled=True)

# STAGE 4: ASSET ACCOUNTING
elif st.session_state.step == 4:
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
        st.session_state.ast_hsa = st.number_input("HSA Balance ($)", min_value=0.0, value=st.session_state.ast_hsa, help="Health Savings Account. The ultimate tax loophole. Money goes in tax-free, grows tax-free, and comes out tax-free for medical expenses.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    total_cash = (st.session_state.ast_checking or 0) + (st.session_state.ast_savings or 0)
    taxable_investments = st.session_state.ast_taxable or 0
    ef_target = com_val * 3
    
    if total_cash < ef_target and taxable_investments > 0:
        st.warning(f"⚠️ **System Observation:** Your cash safety net is underfunded, but you have \${taxable_investments:,.2f} exposed in taxable market accounts. You may need to liquidate investments to fill your cash moat to \${ef_target:,.2f}.")
        
    c2.button("Next", on_click=next_step, type="primary")

# STAGE 5: DEBT DISCOVERY
elif st.session_state.step == 5:
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

# STAGE 6: THE DEBT LEDGER & TIMELINE
elif st.session_state.step == 6:
    st.header("Step 6: The Debt Ledger")
    st.caption("Add your specific liabilities below. The system will categorize them and generate a mathematically optimal payoff timeline.")
    
    # Form to ADD debts (prevents glitching and empty rows)
    with st.form("add_debt_form", clear_on_submit=True):
        st.write("Add a New Liability")
        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        d_name = d_c1.text_input("Name (e.g. Chase Visa)")
        d_bal = d_c2.number_input("Balance ($)", min_value=0.0)
        d_apr = d_c3.number_input("APR (%)", min_value=0.0)
        d_min = d_c4.number_input("Min Payment ($)", min_value=0.0)
        
        submitted = st.form_submit_button("Add to Ledger")
        if submitted and d_name and d_bal > 0 and d_min > 0:
            new_row = pd.DataFrame([{"Debt Name": d_name, "Balance ($)": d_bal, "APR (%)": d_apr, "Min Payment ($)": d_min}])
            st.session_state.debt_df = pd.concat([st.session_state.debt_df, new_row], ignore_index=True)
            st.rerun()

    # Data Editor to MODIFY existing debts
    if not st.session_state.debt_df.empty:
        st.markdown("### Current Ledger (Editable)")
        st.session_state.debt_df = st.data_editor(
            st.session_state.debt_df,
            use_container_width=True,
            hide_index=True,
            key="debt_editor_ui"
        )
        
        # Timeline Math
        temp_df = st.session_state.debt_df.copy()
        temp_df['Balance ($)'] = pd.to_numeric(temp_df['Balance ($)'], errors='coerce').fillna(0)
        temp_df['APR (%)'] = pd.to_numeric(temp_df['APR (%)'], errors='coerce').fillna(0)
        temp_df['Min Payment ($)'] = pd.to_numeric(temp_df['Min Payment ($)'], errors='coerce').fillna(0)
        
        debts_list = temp_df.to_dict('records')
        # Sort by APR descending for Avalanche
        debts_list.sort(key=lambda x: x['APR (%)'], reverse=True)
        
        timeline_results = []
        sim_months = 0
        
        while sum(d['Balance ($)'] for d in debts_list) > 0 and sim_months < 600:
            sim_months += 1
            freed_up_min = 0
            
            # 1. Apply baseline minimums and interest to ALL debts
            for d in debts_list:
                if d['Balance ($)'] > 0:
                    interest = d['Balance ($)'] * (d['APR (%)'] / 100 / 12)
                    d['Balance ($)'] += interest
                    payment = min(d['Min Payment ($)'], d['Balance ($)'])
                    d['Balance ($)'] -= payment
                    if d['Balance ($)'] <= 0.01:
                        d['Balance ($)'] = 0
                        timeline_results.append({"Debt Name": d['Debt Name'], "Months": sim_months, "APR": d['APR (%)']})
                        freed_up_min += d['Min Payment ($)']
                else:
                    freed_up_min += d['Min Payment ($)']
            
            # 2. Avalanche Extra Cash (Margin + Freed Mins) ONLY to Toxic Debt (>= 7%)
            extra_cash = margin + freed_up_min
            for d in debts_list:
                if d['Balance ($)'] > 0 and d['APR (%)'] >= 7.0:
                    payment = min(extra_cash, d['Balance ($)'])
                    d['Balance ($)'] -= payment
                    extra_cash -= payment
                    if d['Balance ($)'] <= 0.01:
                        d['Balance ($)'] = 0
                        timeline_results.append({"Debt Name": d['Debt Name'], "Months": sim_months, "APR": d['APR (%)']})
                    if extra_cash <= 0:
                        break

        if timeline_results:
            st.markdown("### Payoff Timeline")
            st.caption("Visually mapping your exact payoff dates. Notice how we only throw your extra margin at 'Toxic' debt (>= 7%). Low-interest debt receives minimum payments only.")
            
            tl_df = pd.DataFrame(timeline_results)
            tl_df['Payoff Date'] = [datetime.date.today() + pd.DateOffset(months=m) for m in tl_df['Months']]
            tl_df['Payoff Date'] = tl_df['Payoff Date'].dt.strftime('%B %Y')
            tl_df['Strategy Used'] = tl_df['APR'].apply(lambda x: "Avalanche (Aggressive Margin)" if x >= 7.0 else "Minimum Payments Only")
            
            st.dataframe(tl_df[['Debt Name', 'Payoff Date', 'Strategy Used']], use_container_width=True, hide_index=True)
            
            if any(d['APR (%)'] >= 7.0 for d in st.session_state.debt_df.to_dict('records')):
                st.error("🧨 **Your One Next Step: Destroy High-Interest Debt**\n\nYou have toxic debt. You must route 100% of your Guilt-Free Margin directly to the principal of your highest APR debt.\n\n**Action Required:** Leave this app right now. Log into your bank and set up an automatic transfer of **\${margin:,.2f}** to your highest APR debt. You cannot proceed to wealth planning until you change this ledger to reflect $0 balances for all debt over 7% APR.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    
    if not st.session_state.debt_df.empty and any(pd.to_numeric(st.session_state.debt_df['APR (%)'], errors='coerce').fillna(0) >= 7.0):
        c2.button("Clear Toxic Debt to Proceed", disabled=True)
    else:
        c2.button("Next", on_click=next_step, type="primary")

# STAGE 7: SINKING FUNDS
elif st.session_state.step == 7:
    st.header("Step 7: Sinking Funds")
    st.caption("List your predictable non-monthly expenses (Car Registration, Christmas, Vacations). Adding these will actively reduce your Guilt-Free Margin on the left sidebar to ensure you are automatically saving for them.")
    
    with st.form("add_sinking_form", clear_on_submit=True):
        st.write("Add a Non-Monthly Expense")
        sc1, sc2, sc3 = st.columns(3)
        s_name = sc1.text_input("Expense Name")
        s_cost = sc2.number_input("Total Cost ($)", min_value=0.0)
        s_freq = sc3.selectbox("Frequency", ["Annually", "Semi-Annually", "Quarterly"])
        s_sub = st.form_submit_button("Add to Funds")
        if s_sub and s_name and s_cost > 0:
            new_row = pd.DataFrame([{"Expense Name": s_name, "Total Cost ($)": s_cost, "Frequency": s_freq, "Months Until Due": 1}])
            st.session_state.sinking_df = pd.concat([st.session_state.sinking_df, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.sinking_df.empty:
        st.markdown("### Current Sinking Funds (Editable)")
        st.session_state.sinking_df = st.data_editor(
            st.session_state.sinking_df, 
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
    
    if not st.session_state.sinking_df.empty:
        st.info("📅 **Your One Next Step: Automate Sinking Funds**\n\nLog into your bank, open separate checking folders, and set up automated monthly transfers for the bills listed above so they stop surprising you.")
    
    c2.button("Next", on_click=next_step, type="primary")

# STAGE 8: CASH MOAT CHECK
elif st.session_state.step == 8:
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

# STAGE 9: HSA DECISION MATRIX
elif st.session_state.step == 9:
    st.header("Step 9: The HSA Gateway")
    st.caption("Health Savings Accounts are the only accounts in the tax code that are triple-tax-advantaged (tax-free in, tax-free growth, tax-free out). We need to see if you qualify to use one.")
    
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

# STAGE 10: WEALTH ENGINE
elif st.session_state.step == 10:
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
