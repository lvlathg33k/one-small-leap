import streamlit as st
from views import _anchor

YES = "Yes — I'm getting the full match (or my employer doesn't offer one)"
NO = "No — I think I'm leaving some on the table"


def render(next_step, prev_step):
    st.header("Quick gut-check: is there free money on the table?")
    st.markdown(
        "Before we dig into anything else, one fast check. A lot of employers add money to your 401(k) when "
        "you contribute — a dollar-for-dollar match, up to a limit. It's the closest thing to free money that "
        "exists, so it's the *one* thing worth grabbing before we do anything else."
    )

    st.session_state.employer_match = st.radio(
        "Are you currently capturing your full employer 401(k) match?",
        ["Select...", YES, NO],
        help="Not sure? That's incredibly common. Your HR or payroll portal will show your current contribution %, and the match limit is usually listed in your benefits docs.",
    )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)

    if st.session_state.employer_match == NO:
        st.warning(
            "Let's pause here for a second — and honestly, this is good news. 🎁\n\n"
            "Your employer is offering to hand you free money, and right now some of it is quietly walking out "
            "the door. That's not a failure on your part — almost nobody sets this up perfectly on the first try.\n\n"
            f"**Here's the single next move:** open your HR or payroll portal and raise your 401(k) contribution to "
            "at least the match limit (often somewhere around 3–6% of your pay). This protects "
            f"**{_anchor.anchor_phrase()}** more efficiently than almost anything else we'll do today — it's an "
            "instant, guaranteed return.\n\n"
            "Go set it up, then come back and switch your answer. I'll be right here when you return."
        )
    elif st.session_state.employer_match == YES:
        st.success("Perfect — free money captured. That's the highest-return move in all of personal finance, and it's already done. Let's keep going.")
        c2.button("Next", on_click=next_step, type="primary")
    else:
        c2.button("Pick whichever one fits to continue", disabled=True)
