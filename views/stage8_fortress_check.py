import streamlit as st
import pandas as pd
from views import _anchor

TOXIC_APR = 7.0


def _toxic_debt_summary():
    """Return (total_toxic_balance, toxic_debt_count) from the debt ledger."""
    df = st.session_state.get("debt_df")
    if df is None or getattr(df, "empty", True):
        return 0.0, 0
    apr = pd.to_numeric(df.get("APR (%)"), errors="coerce").fillna(0.0)
    bal = pd.to_numeric(df.get("Balance ($)"), errors="coerce").fillna(0.0)
    toxic = (apr >= TOXIC_APR) & (bal > 0)
    return float(bal[toxic].sum()), int(toxic.sum())


def render(next_step, prev_step, com_val, margin):
    st.header("Before we invest — your safety net comes first")
    st.markdown(
        "Here's the order that actually protects you: a cash cushion *before* the stock market. Investing "
        "without a safety net means one bad month — a car repair, a lost shift — can force you to sell at the "
        "worst possible time and undo real progress. A few months of expenses in cash is what lets you pursue "
        f"**{_anchor.anchor_phrase()}** without lying awake at night. The target is about **3 months** of your essentials."
    )

    ef_target = com_val * 3
    checking = st.session_state.ast_checking or 0.0
    savings = st.session_state.ast_savings or 0.0
    taxable = st.session_state.ast_taxable or 0.0
    total_cash = checking + savings

    m1, m2, m3 = st.columns(3)
    m1.metric("3-month safety net target", f"${ef_target:,.2f}")
    m2.metric("Cash you have now", f"${total_cash:,.2f}")
    m3.metric("Money invested (taxable)", f"${taxable:,.2f}")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)

    # ------------------------------------------------------------------
    # UNDERFUNDED: the cushion has a gap.
    # ------------------------------------------------------------------
    if total_cash < ef_target:
        gap = ef_target - total_cash

        if taxable > gap:
            st.subheader("Good news — you can build this cushion faster than you think.")
            st.markdown(
                f"Your cash safety net is short by about **\\${gap:,.2f}**. But here's the thing: you've already got "
                f"**\\${taxable:,.2f}** invested in a regular (taxable) account. That money is doing a job, but "
                "*a safety net is a more important job right now.* You don't have to slowly save your way there over "
                "months — you can shore it up much faster.\n\n"
                "**Something to consider:** move about "
                f"**\\${gap:,.2f}** from your regular investment account into a High-Yield Savings Account, and leave "
                f"the rest (**\\${taxable - gap:,.2f}**) invested and growing. That single move gives you a real "
                f"cushion, so a rough month can't derail **{_anchor.anchor_phrase()}**."
            )
            st.caption("When your cash cushion is topped up, come back to the assets step and update the numbers — then we'll keep going.")
        else:
            st.subheader("Let's build this cushion together, one month at a time.")
            st.markdown(
                f"Your safety net is short by about **\\${gap:,.2f}**, and there aren't enough investments to close "
                "it in one move — that's completely fine, most people build it gradually. For now, your spare cash "
                "has one clear job.\n\n"
                f"**The one next step:** automate a transfer of **\\${margin:,.2f}/mo** into a High-Yield Savings "
                f"Account until the cushion reaches **\\${ef_target:,.2f}**. Every dollar there is a dollar of peace "
                f"of mind protecting **{_anchor.anchor_phrase()}**. Update your cash on the assets step as it grows."
            )
        c2.button("Let's get the safety net funded first", disabled=True)
        return

    # ------------------------------------------------------------------
    # FUNDED: make sure surplus cash isn't quietly losing to inflation.
    # ------------------------------------------------------------------
    surplus = total_cash - ef_target
    toxic_balance, toxic_count = _toxic_debt_summary()

    st.success(f"✅ Your safety net is funded — **\\${total_cash:,.2f}** in cash against a **\\${ef_target:,.2f}** target. That's the foundation. Nicely done.")

    if surplus <= 0.01:
        st.caption("Your cash is right where it should be — protected, not idle. You're cleared to start building. Let's go.")
        c2.button("Next", on_click=next_step, type="primary")
        return

    if toxic_balance > 0:
        st.subheader("Quick math worth pausing on.")
        st.markdown(
            f"You've got about **\\${surplus:,.2f}** in cash beyond your safety net, while also carrying "
            f"**\\${toxic_balance:,.2f}** of high-interest debt. Look at the two rates side by side: that cash is "
            "earning you maybe 4% in savings, while the debt is charging you double digits. Every month, the debt "
            "wins that race.\n\n"
            f"**The move that protects {_anchor.anchor_phrase()}:** send that extra **\\${surplus:,.2f}** straight at "
            "your highest-rate debt. It's a guaranteed return equal to the interest rate you stop paying — no "
            "investment offers that. Once it's applied, update the debt step and we'll continue."
        )
        c2.button("Let's put that cash to work on the debt first", disabled=True)
        return

    # Debt-free with a funded cushion: put the idle surplus to work.
    st.subheader("Let's not let good money sit idle.")
    st.markdown(
        f"You're debt-free with a fully funded safety net — genuinely, that's the hard part done. But you've got "
        f"about **\\${surplus:,.2f}** in extra cash beyond the cushion, and cash slowly loses value to inflation "
        "every year it just sits there. That surplus is ready for a bigger job.\n\n"
        f"**Next up:** we'll put this **\\${surplus:,.2f}**, plus your monthly spare cash, to work building "
        f"**{_anchor.anchor_phrase()}** — in the right order, with the tax-advantaged accounts first."
    )
    c2.button("Let's start building →", on_click=next_step, type="primary")
