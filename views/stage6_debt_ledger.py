import streamlit as st
import pandas as pd
import datetime
from views import _anchor

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
        missing.append("a **name**")
    if balance <= 0:
        missing.append("a **balance** greater than \\$0")
    if minimum <= 0:
        missing.append("a **minimum payment** greater than \\$0")

    if missing:
        st.session_state.debt_form_error = "Almost — this one still needs " + ", ".join(missing) + "."
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


def _delete_row(index):
    """Callback for a row's trash button: remove that single liability."""
    df = st.session_state.debt_df
    if 0 <= index < len(df):
        st.session_state.debt_df = df.drop(df.index[index]).reset_index(drop=True)


def render(next_step, prev_step, margin):
    st.header("Now the debts — all of them, no judgment")
    st.markdown(
        "This is the step people dread, so let's reframe it before we start: **debt isn't a moral failing, "
        "it's just a math problem.** Numbers don't feel shame, and neither should you. The only thing that "
        "actually hurts you is a debt you're *avoiding looking at* — so let's bring every one into the light "
        f"and turn it into a plan for **{_anchor.anchor_phrase()}**."
    )

    st.session_state.setdefault("debt_form_error", "")

    # ------------------------------------------------------------------
    # Add a liability. Form-less: Enter confirms a field; only the button adds.
    # ------------------------------------------------------------------
    st.markdown("**Add a debt**")
    st.caption(
        "Fill in the fields and click **Add to Ledger**. Pressing Enter just confirms the box you're in — "
        "it won't submit the debt, so take your time."
    )
    d_c1, d_c2, d_c3, d_c4 = st.columns(4)
    d_c1.text_input("What is it? (e.g. Chase Visa)", key="new_debt_name")
    d_c2.number_input("Balance ($)", min_value=0.0, step=100.0, key="new_debt_bal")
    d_c3.number_input("Interest rate / APR (%)", min_value=0.0, step=0.1, key="new_debt_apr")
    d_c4.number_input("Minimum payment ($)", min_value=0.0, step=25.0, key="new_debt_min")
    st.button("Add to Ledger", on_click=_add_debt)
    if st.session_state.debt_form_error:
        st.warning(st.session_state.debt_form_error)

    if st.session_state.debt_df.empty:
        st.info("Nothing here yet. Add whatever you're carrying above — or, if you're truly debt-free, just confirm the checklist below and we'll move on.")
    else:
        st.markdown("### Everything you're carrying")
        ledger = st.session_state.debt_df

        # Render the ledger row by row so each line carries its own trash button.
        _COLS = [4, 2.2, 1.6, 2.2, 1.5]
        head = st.columns(_COLS, vertical_alignment="center")
        head[0].markdown("**Debt**")
        head[1].markdown("**Balance**")
        head[2].markdown("**APR**")
        head[3].markdown("**Min Payment**")
        head[4].markdown("**Remove**")

        for i in range(len(ledger)):
            name = str(ledger.iloc[i]["Debt Name"])
            bal = pd.to_numeric(ledger.iloc[i]["Balance ($)"], errors="coerce")
            apr = pd.to_numeric(ledger.iloc[i]["APR (%)"], errors="coerce")
            mn = pd.to_numeric(ledger.iloc[i]["Min Payment ($)"], errors="coerce")
            bal = 0.0 if pd.isna(bal) else float(bal)
            apr = 0.0 if pd.isna(apr) else float(apr)
            mn = 0.0 if pd.isna(mn) else float(mn)

            row = st.columns(_COLS, vertical_alignment="center")
            row[0].write(name)
            row[1].write(f"\\${bal:,.2f}")
            row[2].write(f"{apr:.1f}%")
            row[3].write(f"\\${mn:,.2f}")
            row[4].button(
                "🗑️",
                key=f"del_debt_{i}",
                help=f"Remove {name}",
                on_click=_delete_row,
                args=(i,),
            )

        temp_df = st.session_state.debt_df.copy()
        temp_df["Balance ($)"] = pd.to_numeric(temp_df["Balance ($)"], errors="coerce").fillna(0)
        temp_df["APR (%)"] = pd.to_numeric(temp_df["APR (%)"], errors="coerce").fillna(0)
        temp_df["Min Payment ($)"] = pd.to_numeric(temp_df["Min Payment ($)"], errors="coerce").fillna(0)

        active_records = [r for r in temp_df.to_dict("records") if r["Balance ($)"] > 0]

        if active_records:
            timeline_results, unpaid_debts = _simulate_payoff(active_records, margin)

            if timeline_results:
                st.markdown("### Here's your way out")
                st.caption(
                    f"I ran the math in the background. Your entire **\\${max(margin, 0.0):,.2f}/mo** of spare cash "
                    f"goes at the *most expensive* debts first (anything **{TOXIC_APR:.0f}% APR or higher** — the "
                    f"'toxic' kind), while everything cheaper just gets its minimum. This is the mathematically "
                    "fastest, cheapest way out — the chart shows which debt each strategy is hitting."
                )

                tl_df = pd.DataFrame(timeline_results).sort_values("Months").reset_index(drop=True)
                tl_df["Strategy"] = tl_df["APR (%)"].apply(
                    lambda apr: "Attack first (high interest)" if apr >= TOXIC_APR else "Minimum only (low interest)"
                )
                tl_df["Debt-free by"] = [
                    (datetime.date.today() + pd.DateOffset(months=int(m))).strftime("%b %Y")
                    for m in tl_df["Months"]
                ]

                st.dataframe(
                    tl_df[["Debt Name", "APR (%)", "Strategy", "Months", "Debt-free by"]].rename(
                        columns={"Months": "Months to payoff"}
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
                    "⚠️ One heads-up, gently: the minimum payment on these doesn't even cover the monthly "
                    f"interest, so the balance would keep growing forever: {names_str}. When you can, nudge the "
                    "minimum up a little and they'll start actually shrinking."
                )

            toxic_owed = [
                r for r in temp_df.to_dict("records")
                if r["APR (%)"] >= TOXIC_APR and r["Balance ($)"] > 0
            ]
            if toxic_owed:
                st.subheader("Let's stop the bleeding first.")
                st.markdown(
                    "I'm going to pause us here, the way a good friend would. You're carrying high-interest "
                    "(toxic) debt, and every month it sits there it quietly drains money that belongs to "
                    f"**{_anchor.anchor_phrase()}**. This isn't about guilt — it's about math: no investment "
                    "reliably beats what these rates are charging you, so paying them off *is* the highest-return "
                    "move you can make right now.\n\n"
                    f"**The one next step:** set up an automatic payment of **\\${max(margin, 0.0):,.2f}/mo** toward "
                    "your highest-rate debt (on top of the minimums). Automating it means you never have to rely on "
                    "willpower again.\n\n"
                    f"Once a toxic debt is gone, remove it here with the 🗑️ button. We'll keep going the moment "
                    f"nothing above **{TOXIC_APR:.0f}% APR** is left — that's the gate between cleanup and real wealth building."
                )

    # ------------------------------------------------------------------
    # Debt Discovery checklist — a System-2 slowdown + required gate.
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("One slow, careful pass — did we miss anything?")
    st.markdown(
        "The debts that hurt most are the ones we mentally file away and never look at. So let's deliberately "
        "slow down and check **every** category — not to make you feel bad, but so nothing can ambush you later. "
        "Tick **all** of the boxes below once you've confirmed each one (either you listed it above, or you're "
        "genuinely at zero)."
    )
    st.session_state.cc_check = st.checkbox(
        "Credit cards — Chase, Amex, Capital One, store/retail cards, all of them", value=st.session_state.cc_check
    )
    st.session_state.auto_check = st.checkbox(
        "Auto loans, leases, or recreational-vehicle notes", value=st.session_state.auto_check
    )
    st.session_state.student_check = st.checkbox(
        "Student loans — federal or private", value=st.session_state.student_check
    )
    st.session_state.mortgage_check = st.checkbox(
        "Mortgage, HELOC, or other real-estate loans", value=st.session_state.mortgage_check
    )
    st.markdown(
        "*Take a breath before this last one.* Buy-now-pay-later and payday loans are the ones people most often "
        "leave off — not because they forget, but because there's shame attached. There shouldn't be: they're "
        "engineered to be easy to start and easy to lose track of. You're not behind; you're just doing the brave "
        "thing and looking directly at them."
    )
    st.session_state.payday_check = st.checkbox(
        "Payday loans, personal loans, or Buy-Now-Pay-Later (Klarna, Affirm, Afterpay, Speedy Cash, etc.)",
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
        c2.button("Knock out the toxic debt first, then we continue", disabled=True)
    elif not all_acknowledged:
        c2.button("Check all the boxes above to continue", disabled=True)
    else:
        c2.button("Next", on_click=next_step, type="primary")
