import streamlit as st
from views import _anchor


def render(next_step, prev_step):
    st.header("First, let's see what you're working with")
    st.markdown(
        "No budgeting lecture, I promise. We just need to know how much fuel you've got for the journey toward "
        f"**{_anchor.anchor_phrase()}**. Every plan we build sits on top of this one number, so let's get it right."
    )

    st.session_state.take_home = st.number_input(
        "How much actually lands in your account each month, after taxes?",
        min_value=0.0,
        step=100.0,
        value=st.session_state.take_home,
        help=(
            "Grab a recent paystub and find your 'Net Pay' — the amount that actually hits your checking "
            "account after taxes and deductions. Paid every two weeks? Multiply one check by 2.17 for a monthly number."
        ),
    )
    st.caption(
        "This is your real take-home — the actual fuel we get to work with. We'll never ask you to "
        "white-knuckle a budget. We'll just make sure this fuel flows toward what matters to you."
    )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    if st.session_state.take_home is not None and st.session_state.take_home > 0:
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Add your take-home pay to keep going", disabled=True)
