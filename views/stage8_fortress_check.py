import streamlit as st
import pandas as pd

TOXIC_APR = 7.0


def _toxic_debt_summary():
    """Return (total_toxic_balance, toxic_debt_count) from the debt ledger.

    Toxic debt is any liability with an APR at or above TOXIC_APR. The ledger is
    user-editable, so every value is coerced defensively before it is trusted.
    """
    df = st.session_state.get("debt_df")
    if df is None or getattr(df, "empty", True):
        return 0.0, 0
    apr = pd.to_numeric(df.get("APR (%)"), errors="coerce").fillna(0.0)
    bal = pd.to_numeric(df.get("Balance ($)"), errors="coerce").fillna(0.0)
    toxic = (apr >= TOXIC_APR) & (bal > 0)
    return float(bal[toxic].sum()), int(toxic.sum())


def render(next_step, prev_step, com_val, margin):
    st.header("Step 7: The Fortress Check")
    st.caption(
        "Before we expose a single dollar to the market, your cash moat must be exactly right — "
        "not too thin, not bloated. Underfunded cash is fragility. Excess idle cash is a slow, "
        "guaranteed loss to inflation. We fix both here."
    )

    ef_target = com_val * 3
    checking = st.session_state.ast_checking or 0.0
    savings = st.session_state.ast_savings or 0.0
    taxable = st.session_state.ast_taxable or 0.0
    total_cash = checking + savings

    m1, m2, m3 = st.columns(3)
    m1.metric("3-Month Survival Target", f"${ef_target:,.2f}")
    m2.metric("Current Liquid Cash", f"${total_cash:,.2f}")
    m3.metric("Taxable Brokerage", f"${taxable:,.2f}")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)

    # ------------------------------------------------------------------
    # UNDERFUNDED: the moat has a gap. This is a hard stop.
    # ------------------------------------------------------------------
    if total_cash < ef_target:
        gap = ef_target - total_cash

        if taxable > gap:
            # Reallocation directive: the gap can be closed today by liquidating
            # unprotected market exposure instead of saving for months.
            st.error("🛡️ **CRITICAL: FUND THE MOAT FROM YOUR BROKERAGE — DO NOT PROCEED**")
            st.markdown(
                f"Your cash safety net is short by **\\${gap:,.2f}**, yet you are holding "
                f"**\\${taxable:,.2f}** exposed in a taxable brokerage account. "
                "You will not save your way out of this over months. You will close it today."
            )
            st.markdown(
                f"1. Sell **\\${gap:,.2f}** of your taxable brokerage holdings.\n"
                f"2. Move the proceeds into your High-Yield Savings Account (HYSA).\n"
                f"3. Leave the remaining **\\${taxable - gap:,.2f}** invested and working.\n"
                f"4. Return to Step 4 and update your liquid cash to **\\${ef_target:,.2f}**."
            )
            st.caption(
                "Market exposure without a cash moat is gambling. Liquidate the exposure, "
                "seal the moat, then come back."
            )
        else:
            # Not enough taxable to close the gap: the margin must fund it.
            st.error("🛡️ **CRITICAL: BUILD THE FORTRESS — DO NOT PROCEED**")
            st.markdown(
                f"Your safety net is short by **\\${gap:,.2f}**, and your brokerage cannot cover the gap. "
                "Every dollar of Guilt-Free Margin now has exactly one job: fill this vault.\n\n"
                "**Action Required:** Leave this app. Automate a "
                f"**\\${margin:,.2f}** monthly transfer into your HYSA. Return to Step 4 and update "
                f"your balance once liquid cash reaches **\\${ef_target:,.2f}**."
            )
        c2.button("Fill Fortress to Proceed", disabled=True)
        return

    # ------------------------------------------------------------------
    # FUNDED: verify we are not bleeding surplus cash to inflation.
    # ------------------------------------------------------------------
    surplus = total_cash - ef_target
    toxic_balance, toxic_count = _toxic_debt_summary()

    st.success(f"✅ Fortress funded: **\\${total_cash:,.2f}** liquid against a **\\${ef_target:,.2f}** target.")

    if surplus <= 0.01:
        st.caption("Your cash position is precise. No idle capital detected. You are cleared for wealth generation.")
        c2.button("Next", on_click=next_step, type="primary")
        return

    if toxic_balance > 0:
        # Surplus cash sitting idle while double-digit debt compounds is a
        # guaranteed loss. Hard stop until it is deployed against the debt.
        st.error("🧨 **CRITICAL: DEPLOY SURPLUS AGAINST TOXIC DEBT — DO NOT PROCEED**")
        st.markdown(
            f"You are sitting on **\\${surplus:,.2f}** of surplus cash above your moat while carrying "
            f"**\\${toxic_balance:,.2f}** across **{toxic_count}** high-interest "
            f"(≥ {TOXIC_APR:.0f}% APR) liability(ies). Cash earning ~4% while debt compounds against "
            "you at double digits is a math failure, not a safety cushion.\n\n"
            "**Action Required:** Leave this app. Transfer the full "
            f"**\\${surplus:,.2f}** surplus to the principal of your highest-APR debt, then return "
            "to Step 5 and update the ledger."
        )
        c2.button("Deploy Surplus to Proceed", disabled=True)
        return

    # Debt-free with a funded moat: push the idle surplus into the Wealth Engine.
    st.warning("⚔️ **DIRECTIVE: DEPLOY IDLE SURPLUS INTO THE WEALTH ENGINE**")
    st.markdown(
        f"You are debt-free with a fully funded moat, but **\\${surplus:,.2f}** is sitting above your "
        "target and decaying to inflation every month it stays in cash. Cash beyond your moat is not "
        "safety — it is a slow, silent loss.\n\n"
        f"**Your move:** Carry this **\\${surplus:,.2f}** into Step 9 and deploy it through the Capital "
        "Allocation Waterfall alongside your monthly margin. Advance now."
    )
    c2.button("Next", on_click=next_step, type="primary")
