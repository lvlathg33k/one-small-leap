import streamlit as st
from views import _anchor


def render(next_step, prev_step, com_val):
    st.header("Let's empty your pockets — the good stuff first")
    st.markdown(
        "Now we take gentle inventory of what you already have. This isn't a test, and you don't need exact "
        "numbers — rough is fine. Don't have one of these accounts? Just leave it blank and move on. "
        "Tap the **?** next to anything you're unsure about for a plain-English explanation."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cash you can reach")
        st.session_state.ast_checking = st.number_input("Checking account(s) ($)", min_value=0.0, value=st.session_state.ast_checking, help="Where your paycheck lands and your daily bills get paid from.")
        st.session_state.ast_savings = st.number_input("Savings account(s) ($)", min_value=0.0, value=st.session_state.ast_savings, help="Cash set aside for emergencies or short-term goals. Ideally in a High-Yield Savings Account (HYSA) that pays you real interest.")

        st.subheader("Your home")
        st.session_state.ast_home = st.number_input("Estimated home value ($)", min_value=0.0, value=st.session_state.ast_home, help="A rough estimate of what your home is worth today. Just the value — don't subtract your mortgage.")

    with col2:
        st.subheader("Money that's invested")
        st.session_state.ast_taxable = st.number_input("Regular investment account ($)", min_value=0.0, value=st.session_state.ast_taxable, help="A standard brokerage account (think Robinhood, Fidelity, Vanguard) that isn't a retirement account.")
        st.session_state.ast_trad_ira = st.number_input("Traditional IRA / 401(k) ($)", min_value=0.0, value=st.session_state.ast_trad_ira, help="Retirement accounts you funded pre-tax. You get a tax break now and pay taxes when you withdraw in retirement.")
        st.session_state.ast_roth_ira = st.number_input("Roth IRA / Roth 401(k) ($)", min_value=0.0, value=st.session_state.ast_roth_ira, help="Retirement accounts where you already paid the taxes — the growth and withdrawals come out completely tax-free.")
        st.session_state.ast_hsa = st.number_input("HSA balance ($)", min_value=0.0, value=st.session_state.ast_hsa, help="Health Savings Account. The rare triple win: money goes in tax-free, grows tax-free, and comes out tax-free for medical costs.")

    st.divider()

    total_cash = (st.session_state.ast_checking or 0) + (st.session_state.ast_savings or 0)
    taxable_investments = st.session_state.ast_taxable or 0
    ef_target = com_val * 3

    if total_cash < ef_target and taxable_investments > 0:
        st.info(
            f"👀 Something I noticed — no need to act on it yet. Your cash cushion is a bit thin, but you've got "
            f"about **\\${taxable_investments:,.2f}** sitting in investments. Hold that thought; in a couple of steps "
            f"we'll look at whether moving some of it into a proper safety net (around **\\${ef_target:,.2f}**) would "
            "give you more peace of mind. We'll decide that together."
        )

    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("Next", on_click=next_step, type="primary")
