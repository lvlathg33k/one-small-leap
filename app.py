import streamlit as st
import pandas as pd
from views import (
    stage0_setup,
    stage1_income,
    stage2_match,
    stage3_expenses,
    stage4_assets,
    stage6_debt_ledger,
    stage7_sinking_funds,
    stage8_fortress_check,
    stage9_hsa,
    stage10_wealth_engine
)

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
    for key in list(st.session_state.keys()):
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
    st.markdown(f"**Total Take-Home**<br><span style='color: #4da6ff; font-size: 24px; font-weight: bold;'>\\${th_val:,.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Committed Money**<br><span style='color: #cc0000; font-size: 24px; font-weight: bold;'>\\${com_val:,.2f}</span>", unsafe_allow_html=True)
    if sinking_monthly > 0:
        st.caption(f"(Includes \\${sinking_monthly:,.2f} automated sinking funds)")
    
    margin_color = "#00cc44" if margin > 0 else "#ff3333"
    margin_label = "Guilt-Free Margin" if margin > 0 else "Liquidity Deficit"
    st.markdown(f"**{margin_label}**<br><span style='color: {margin_color}; font-size: 24px; font-weight: bold;'>\\${margin:,.2f}</span>", unsafe_allow_html=True)
    
    st.divider()
    total_steps = 9
    st.progress(min((st.session_state.step) / total_steps, 1.0))
    st.caption(f"Stage {st.session_state.step} of {total_steps}")

# ==========================================
# ROUTER
# ==========================================
if st.session_state.step == 0:
    stage0_setup.render(next_step, prev_step)
elif st.session_state.step == 1:
    stage1_income.render(next_step, prev_step)
elif st.session_state.step == 2:
    stage2_match.render(next_step, prev_step)
elif st.session_state.step == 3:
    stage3_expenses.render(next_step, prev_step, margin)
elif st.session_state.step == 4:
    stage4_assets.render(next_step, prev_step, com_val)
elif st.session_state.step == 5:
    stage6_debt_ledger.render(next_step, prev_step, margin)
elif st.session_state.step == 6:
    stage7_sinking_funds.render(next_step, prev_step)
elif st.session_state.step == 7:
    stage8_fortress_check.render(next_step, prev_step, com_val, margin)
elif st.session_state.step == 8:
    stage9_hsa.render(next_step, prev_step)
elif st.session_state.step == 9:
    stage10_wealth_engine.render(next_step, prev_step, reset, margin)
