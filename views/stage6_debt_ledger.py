import streamlit as st
import pandas as pd
import datetime

TOXIC_APR = 7.0
MAX_SIM_MONTHS = 600

# Keys for the (deliberately form-less) add-liability inputs. Living outside an
# st.form means pressing Enter in a field only confirms that field — it never
# submits the liability. Only the "Add to Ledger" button does that.
_INPUT_DEFAULTS = {
    "new_debt_name": "",
    "new_debt_bal": 0.0,
    "new_debt_apr": 0.0,
    "new_debt_min": 0.0,
}


def _simulate_payoff(debt_records, margin):
    """Run the Avalanche simulation.

    Rules:
      * Every debt receives its minimum payment each month.
      * Guilt-Free Margin (plus any minimums freed by cleared debts) is thrown
        ONLY at debts with an APR >= TOXIC_APR, highest APR first.
      * Debts under TOXIC_APR receive minimum payments only.

    Returns (timeline_results, unpaid_debts).
    """
    debts = []
    for rec in debt_records:
        debts.append({
            "name": rec["Debt Name"],
            "balance": float(rec["Balance ($)"]),
            "apr": float(rec["APR (%)"]),
            "minimum": float(rec["Min Payment ($)"]),
        })

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

        for d in debts:
            if d["balance"] > 0:
                d["balance"] += d["balance"] * (d["apr"] / 100.0 / 12.0)
                payment = min(d["minimum"], d["balance"])
                d["balance"] -= payment
                if d["balance"] <= 0.01:
                    record_payoff(d, months)
                    freed_up += d["minimum"]
            else:
                freed_up += d["minimum"]

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


def _add_debt():
    """Callback for the 'Add to Ledger' button.

    Runs ONLY on an explicit button click, never on an Enter keystroke, because
    the inputs are not wrapped in an st.form. Validates strictly, then appends.
    """
    name = (st.session_state.new_debt_name or "").strip()
    balance = st.session_state.new_debt_bal or 0.0
    apr = st.session_state.new_debt_apr or 0.0
    minimum = st.session_state.new_debt_min or 0.0

    missing = []
    if not name:
        missing.append("a **Name**")
    if balance <= 0:
        missing.append("a **Balance** greater than \\$0")
    if minimum <= 0:
        missing.append("a **Minimum Payment** greater than \\$0")

    if missing:
        st.session_state.debt_form_error = "Rejected. Every liability requires " + ", ".join(missing) + "."
        return

    new_row = pd.DataFrame([{
        "Debt Name": name,
        "Balance ($)": float(balance),
        "APR (%)": float(apr),
        "Min Payment ($)": float(minimum),
    }])
    st.session_state.debt_df = pd.concat([st.session_state.debt_df, new_row], ignore_index=True)
    st.session_state.debt_form_error = ""

    # Reset the inputs for the next entry (allowed inside a callback).
    for key, default in _INPUT_DEFAULTS.items():
        st.session_state[key] = default


def _delete_debts():
    """Callback to remove the selected liabilities from the ledger."""
    idxs = st.session_state.get("debt_delete_select", [])
    if idxs:
        st.session_state.debt_df = (
            st.session_state.debt_df.drop(index=idxs, errors="ignore").reset_index(drop=True)
        )
    st.session_state.debt_delete_select = []


def render(next_step, prev_step, margin):
    st.header("Step 5: The Debt Ledger")
    st.caption(
        "Log every liability. The system sorts them by threat level and builds a mathematically "
        "optimal payoff order: we attack high-interest debt with your entire margin and pay "
        "everything else the minimum only."
    )

    st.session_state.setdefault("debt_form_error", "")

    # ------------------------------------------------------------------
    # Add a liability. Form-less: Enter confirms a field; only the button adds.
    # ------------------------------------------------------------------
    st.markdown("**Add a New Liability**")
    st.caption(
        "Fill the fields, then click **Add to Ledger**. Pressing Enter only confirms the field "
        "you're editing — it will not submit the liability."
    )
    d_c1, d_c2, d_c3, d_c4 = st.columns(4)
    d_c1.text_input("Name (e.g. Chase Visa)", key="new_debt_name")
    d_c2.number_input("Balance ($)", min_value=0.0, step=100.0, key="new_debt_bal")
    d_c3.number_input("APR (%)", min_value=0.0, step=0.1, key="new_debt_apr")
    d_c4.number_input("Min Payment ($)", min_value=0.0, step=25.0, key="new_debt_min")
    st.button("Add to Ledger", on_click=_add_debt)
    if st.session_state.debt_form_error:
        st.error(st.session_state.debt_form_error)

    if st.session_state.debt_df.empty:
        st.info("No liabilities logged yet. Add one above, or confirm the checklist below if you are debt-free.")
    else:
        st.markdown("### Current Ledger (Editable)")
        # Key varies with row count so structural changes (add/delete) reset the
        # grid cleanly; inline edits within a stable row count still persist.
        st.session_state.debt_df = st.data_editor(
            st.session_state.debt_df,
            use_container_width=True,
            hide_index=True,
            key=f"debt_editor_ui_{len(st.session_state.debt_df)}",
        )

        # Explicit delete control (keeps the grid add-proof so the validated
        # button stays the only way to CREATE a liability).
        names = st.session_state.debt_df["Debt Name"].tolist()
        del_c1, del_c2 = st.columns([5, 1])
        del_c1.multiselect(
            "Delete a liability",
            options=list(range(len(names))),
            format_func=lambda i: names[i],
            key="debt_delete_select",
            placeholder="Select one or more liabilities to remove",
        )
        del_c2.button(
            "🗑️ Delete",
            on_click=_delete_debts,
            use_container_width=True,
            disabled=not st.session_state.get("debt_delete_select"),
        )

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

                st.bar_chart(tl_df, x="Debt Name", y="Months", color="Strategy")

            if unpaid_debts:
                names_str = ", ".join(f"**{d['name']}**" for d in unpaid_debts)
                st.warning(
                    "⚠️ These liabilities never amortize because the minimum payment does not even "
                    f"cover monthly interest: {names_str}. Raise the minimum payment or the balance will "
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

    # ------------------------------------------------------------------
    # Debt Discovery checklist — a required check to leave the ledger page.
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Debt Discovery Checklist")
    st.caption(
        "Before moving on, confirm you have accounted for **ALL** potential liabilities. Check "
        "**ALL** boxes below — each one confirms you either carry that balance or verified it is zero."
    )
    st.session_state.cc_check = st.checkbox(
        "Credit Cards (Chase, Amex, Capital One, Store/Retail cards, etc.)", value=st.session_state.cc_check
    )
    st.session_state.auto_check = st.checkbox(
        "Auto Loans, Leases, or Recreational Vehicle notes", value=st.session_state.auto_check
    )
    st.session_state.student_check = st.checkbox(
        "Student Loans (Federal or Private)", value=st.session_state.student_check
    )
    st.session_state.mortgage_check = st.checkbox(
        "Mortgages, HELOCs, or other real estate loans", value=st.session_state.mortgage_check
    )
    st.session_state.payday_check = st.checkbox(
        "Payday Loans, Personal Loans, or 'Buy Now, Pay Later' (e.g., Klarna, Affirm, Speedy Cash)",
        value=st.session_state.payday_check,
    )
    all_acknowledged = (
        st.session_state.cc_check and st.session_state.auto_check and st.session_state.student_check
        and st.session_state.mortgage_check and st.session_state.payday_check
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
    elif not all_acknowledged:
        c2.button("Acknowledge all categories to continue", disabled=True)
    else:
        c2.button("Next", on_click=next_step, type="primary")
