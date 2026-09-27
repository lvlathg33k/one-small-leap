import streamlit as st
import pandas as pd


def render(next_step, prev_step):
    st.header("The expenses that ambush you")
    st.markdown(
        "You know the ones — car registration, the holidays, insurance that hits once a year, a vacation you "
        "actually want to take. They're not emergencies; they're *predictable*. The only reason they feel like "
        "emergencies is that nobody set the money aside in advance. Let's fix that so you're never blindsided again."
    )
    st.caption(
        "For anything you add, we quietly set aside a slice each month (a 'sinking fund'). You'll see your "
        "spare cash on the left adjust to reflect it — that's on purpose, so the money is already there when the bill lands."
    )

    with st.form("add_sinking_form", clear_on_submit=True):
        st.write("Add a predictable, non-monthly expense")
        sc1, sc2, sc3 = st.columns(3)
        s_name = sc1.text_input("What is it? (e.g. Car registration)")
        s_cost = sc2.number_input("What does it cost each time? ($)", min_value=0.0)
        s_freq = sc3.selectbox("How often?", ["Annually", "Semi-Annually", "Quarterly"])
        s_sub = st.form_submit_button("Set it aside")
        if s_sub and s_name and s_cost > 0:
            new_row = pd.DataFrame([{"Expense Name": s_name, "Total Cost ($)": s_cost, "Frequency": s_freq, "Months Until Due": 1}])
            st.session_state.sinking_df = pd.concat([st.session_state.sinking_df, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.sinking_df.empty:
        st.markdown("### What you're now saving for (editable)")
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
        st.info(
            "📅 **One small next step, whenever you're ready:** open a separate savings 'bucket' at your bank and "
            "set up an automatic monthly transfer for the amounts above. Once it's automated, these bills stop "
            "being scary surprises and become boring, handled non-events. That's exactly what we're going for."
        )

    c2.button("Next", on_click=next_step, type="primary")
