import streamlit as st
import pandas as pd
import datetime

def render(next_step, prev_step, margin):
    st.header("Step 6: The Debt Ledger")
    st.caption("Add your specific liabilities below. The system will categorize them and generate a mathematically optimal payoff timeline.")
    
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

    if not st.session_state.debt_df.empty:
        st.markdown("### Current Ledger (Editable)")
        st.session_state.debt_df = st.data_editor(
            st.session_state.debt_df,
            use_container_width=True,
            hide_index=True,
            key="debt_editor_ui"
        )
        
        temp_df = st.session_state.debt_df.copy()
        temp_df['Balance ($)'] = pd.to_numeric(temp_df['Balance ($)'], errors='coerce').fillna(0)
        temp_df['APR (%)'] = pd.to_numeric(temp_df['APR (%)'], errors='coerce').fillna(0)
        temp_df['Min Payment ($)'] = pd.to_numeric(temp_df['Min Payment ($)'], errors='coerce').fillna(0)
        
        debts_list = temp_df.to_dict('records')
        debts_list.sort(key=lambda x: x['APR (%)'], reverse=True)
        
        timeline_results = []
        sim_months = 0
        
        while sum(d['Balance ($)'] for d in debts_list) > 0 and sim_months < 600:
            sim_months += 1
            freed_up_min = 0
            
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
