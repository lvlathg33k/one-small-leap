import streamlit as st


def render(next_step, prev_step):
    st.header("One quick health-plan question")
    st.markdown(
        "Almost there — this one just tunes the plan to you. If you're on a specific type of health insurance, "
        "you get access to the single most tax-friendly account in existence (an HSA). If not, no worries at all — "
        "we'll simply route around it."
    )

    st.session_state.hdhp_status = st.radio(
        "Are you on a High-Deductible Health Plan (HDHP) at work?",
        ["Select...", "Yes, I'm on an HDHP", "No / not sure — I have a standard plan (PPO, HMO, etc.)"],
        help="An HDHP is a health plan with a higher deductible in exchange for lower premiums. If you have an HSA available through work, you're almost certainly on one. If you're unsure, the second option is the safe pick.",
    )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)

    if st.session_state.hdhp_status == "Select...":
        c2.button("Pick one to continue", disabled=True)
    else:
        if st.session_state.hdhp_status == "Yes, I'm on an HDHP":
            st.success(
                "💡 Nice — that unlocks the HSA, the only account that's tax-free going in, growing, *and* coming "
                "out (for medical costs). Your plan on the next screen will fill it first. Insider move: if you can "
                "afford to, pay today's medical bills out of pocket, save the receipts, and let the HSA money grow "
                "invested — you can reimburse yourself tax-free years later."
            )
        else:
            st.info(
                "💡 Totally fine — most people aren't on an HDHP. We'll simply skip the HSA and send your money "
                "straight to the next-best homes: your Roth IRA and 401(k). Nothing lost."
            )
        c2.button("Next", on_click=next_step, type="primary")
