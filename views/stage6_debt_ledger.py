import streamlit as st
import pandas as pd
import datetime

TOXIC_APR = 7.0
MAX_SIM_MONTHS = 600


def _simulate_payoff(debt_records, margin):
    """Run the Avalanche simulation.

    Rules:
      * Every debt receives its minimum payment each month.
      * Guilt-Free Margin (plus any minimums freed by cleared debts) is thrown
        ONLY at debts with an APR >= TOXIC_APR, highest APR first.
      * Debts under TOXIC_APR receive minimum payments only.

    Returns (timeline_results, unpaid_debts). ``timeline_results`` is a list of
    dicts with the month each debt is cleared; ``unpaid_debts`` are debts whose
    minimum payment never overcomes interest within the simulation horizon.
    """
    debts = []
    for rec in debt_records:
        debts.append({
            "name": rec["Debt Name"],
            "balance": float(rec["Balance ($)"]),
            "apr": float(rec["APR (%)"]),
            "minimum": float(rec["Min Payment ($)"]),
        })

    # Attack highest APR first (Avalanche ordering).
    debts.sort(key=lambda d: d["apr"], reverse=True)

    timeline_results = []
    cleared = set()
    extra_margin = max(margin, 0.0)
    months = 0

    def record_payoff(debt, month):
        if debt["name"] not in cleared:
            debt["balance"] = 0.0
            cleared.add(debt["name"])
            timeline_results.append({
                "Debt Name": debt["name"],
                "APR (%)": debt["apr"],
                "Months": month,
            })

    while sum(d["balance"] for d in debts) > 0.01 and months < MAX_SIM_MONTHS:
        months += 1
        freed_up = 0.0

        # 1) Accrue interest and apply every minimum payment.
        for d in debts:
            if d["balance"] > 0:
                d["balance"] += d["balance"] * (d["apr"] / 100.0 / 12.0)
                payment = min(d["minimum"], d["balance"])
                d["balance"] -= payment
                if d["balance"] <= 0.01:
                    record_payoff(d, months)
                    freed_up += d["minimum"]
            else:
                # Already-cleared debts roll their old minimum into the attack.
                freed_up += d["minimum"]

        # 2) Throw margin + freed minimums at toxic debt only, highest APR first.
        attack_cash = extra_margin + freed_up
        for d in debts:
            if attack_cash <= 0:
                break
            if d["balance"] > 0 and d["apr"] >= TOXIC_APR:
                payment = min(attack_cash, d["balance"])
                d["balance"] -= payment
                attack_cash -= payment
                if d["balance"] <= 0.01:
                    record_payoff(d, months)

    unpaid_debts = [d for d in debts if d["balance"] > 0.01]
    return timeline_results, unpaid_debts


def render(next_step, prev_step, margin):
    st.header("Step 6: The Debt Ledger")
    st.caption(
        "Log every liability. The system sorts them by threat level and builds a mathematically "
        "optimal payoff order: we attack high-interest debt with your entire margin and pay "
        "everything else the minimum only."
    )

    # ------------------------------------------------------------------
    # Add-a-liability form. Strictly requires Name, Balance > 0, Min > 0.
    # ------------------------------------------------------------------
    with st.form("add_debt_form", clear_on_submit=True):
        st.write("**Add a New Liability**")
        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        d_name = d_c1.text_input("Name (e.g. Chase Visa)")
        d_bal = d_c2.number_input("Balance ($)", min_value=0.0, step=100.0)
        d_apr = d_c3.number_input("APR (%)", min_value=0.0, step=0.1)
        d_min = d_c4.number_input("Min Payment ($)", min_value=0.0, step=25.0)
        submitted = st.form_submit_button("Add to Ledger")

    if submitted:
        clean_name = (d_name or "").strip()
        missing = []
        if not clean_name:
            missing.append("a **Name**")
        if d_bal <= 0:
            missing.append("a **Balance** greater than \\$0")
        if d_min <= 0:
            missing.append("a **Minimum Payment** greater than \\$0")

        if missing:
            st.error("Rejected. Every liability requires " + ", ".join(missing) + ".")
        else:
            new_row = pd.DataFrame([{
                "Debt Name": clean_name,
                "Balance ($)": float(d_bal),
                "APR (%)": float(d_apr),
                "Min Payment ($)": float(d_min),
            }])
            st.session_state.debt_df = pd.concat([st.session_state.debt_df, new_row], ignore_index=True)
            st.rerun()

    if st.session_state.debt_df.empty:
        st.info("No liabilities logged yet. Add one above, or advance if you are debt-free.")
    else:
        st.markdown("### Current Ledger (Editable)")
        st.session_state.debt_df = st.data_editor(
            st.session_state.debt_df,
            use_container_width=True,
            hide_index=True,
            key="debt_editor_ui",
        )

        # Coerce the user-editable grid into clean numbers before simulating.
        temp_df = st.session_state.debt_df.copy()
        temp_df["Balance ($)"] = pd.to_numeric(temp_df["Balance ($)"], errors="coerce").fillna(0)
        temp_df["APR (%)"] = pd.to_numeric(temp_df["APR (%)"], errors="coerce").fillna(0)
        temp_df["Min Payment ($)"] = pd.to_numeric(temp_df["Min Payment ($)"], errors="coerce").fillna(0)

        active_records = [r for r in temp_df.to_dict("records") if r["Balance ($)"] > 0]

        if active_records:
            timeline_results, unpaid_debts = _simulate_payoff(active_records, margin)

            if timeline_results:
                st.markdown("### Payoff Timeline")
                st.caption(
                    f"Your entire **\\${max(margin, 0.0):,.2f}** Guilt-Free Margin is routed at debts of "
                    f"**{TOXIC_APR:.0f}% APR or higher** (Avalanche). Anything below "
                    f"**{TOXIC_APR:.0f}%** receives minimum payments only — the chart labels which "
                    "strategy hits which debt."
                )

                tl_df = pd.DataFrame(timeline_results).sort_values("Months").reset_index(drop=True)
                tl_df["Strategy"] = tl_df["APR (%)"].apply(
                    lambda apr: "Avalanche (Margin Attack)" if apr >= TOXIC_APR else "Minimum Only"
                )
                tl_df["Payoff Date"] = [
                    (datetime.date.today() + pd.DateOffset(months=int(m))).strftime("%b %Y")
                    for m in tl_df["Months"]
                ]

                st.dataframe(
                    tl_df[["Debt Name", "APR (%)", "Strategy", "Months", "Payoff Date"]].rename(
                        columns={"Months": "Months to Payoff"}
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "APR (%)": st.column_config.NumberColumn("APR (%)", format="%.1f%%"),
                    },
                )

                # Explicit visual: bars grouped/colored by the strategy applied.
                st.bar_chart(tl_df, x="Debt Name", y="Months", color="Strategy")

            if unpaid_debts:
                names = ", ".join(f"**{d['name']}**" for d in unpaid_debts)
                st.warning(
                    "⚠️ These liabilities never amortize because the minimum payment does not even "
                    f"cover monthly interest: {names}. Raise the minimum payment or the balance will "
                    "grow forever."
                )

            toxic_owed = [
                r for r in temp_df.to_dict("records")
                if r["APR (%)"] >= TOXIC_APR and r["Balance ($)"] > 0
            ]
            if toxic_owed:
                st.error(
                    "🧨 **Your One Next Step: Destroy High-Interest Debt**\n\n"
                    "You are carrying toxic debt. Route 100% of your Guilt-Free Margin at the "
                    "principal of your highest-APR debt — nothing else moves until it is gone.\n\n"
                    f"**Action Required:** Leave this app. Automate a **\\${max(margin, 0.0):,.2f}** "
                    "monthly transfer to your highest-APR debt. You cannot proceed to wealth planning "
                    "until this ledger shows \\$0 for every liability at or above "
                    f"{TOXIC_APR:.0f}% APR."
                )

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)

    if st.session_state.debt_df.empty:
        has_toxic_debt = False
    else:
        apr_series = pd.to_numeric(st.session_state.debt_df["APR (%)"], errors="coerce").fillna(0)
        bal_series = pd.to_numeric(st.session_state.debt_df["Balance ($)"], errors="coerce").fillna(0)
        has_toxic_debt = bool(((apr_series >= TOXIC_APR) & (bal_series > 0)).any())

    if has_toxic_debt:
        c2.button("Clear Toxic Debt to Proceed", disabled=True)
    else:
        c2.button("Next", on_click=next_step, type="primary")
