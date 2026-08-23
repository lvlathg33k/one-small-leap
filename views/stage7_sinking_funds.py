import streamlit as st
import pandas as pd

def render(next_step, prev_step):
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
