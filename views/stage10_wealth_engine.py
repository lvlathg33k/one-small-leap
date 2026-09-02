import streamlit as st
import pandas as pd
import datetime
import math

ANNUAL_RATE = 0.07
MAX_TRAJECTORY_MONTHS = 1200  # 100-year cap keeps the chart bounded.


def render(next_step, prev_step, reset, margin):
    st.header("Step 9: The Wealth Engine")
    st.caption(
        "You survived the gauntlet: zero toxic debt, a fully funded moat, automated sinking funds. "
        "Now deploy your unallocated margin into wealth generation — in the correct order, every time."
    )

    st.markdown("### The Capital Allocation Waterfall")
    st.markdown(
        "Fill each tier to its statutory limit before deploying a single dollar to the next. "
        "*This assumes you are already capturing your full 401(k) match from Step 2 — that is free "
        "money and it comes before everything below.*"
    )

    has_hsa = st.session_state.hdhp_status == "Yes, I have an HDHP"
    tier = 1

    if has_hsa:
        st.markdown(
            f"**{tier}. Health Savings Account (HSA) — 2025 limit: \\$4,300 self-only / \\$8,550 family "
            "(+\\$1,000 catch-up at age 55+).** The only triple-tax-advantaged account there is. Invest "
            "it in broad-market funds. Do NOT spend it on current medical bills — pay those in cash, "
            "keep the receipts, and let this compound."
        )
        tier += 1

    st.markdown(
        f"**{tier}. Roth IRA — 2025 limit: \\$7,000/yr (\\$8,000 if age 50+).** Tax-free growth, "
        "tax-free withdrawals. Invest in low-cost, broad-market index funds."
    )
    tier += 1

    st.markdown(
        f"**{tier}. Max out your 401(k) — 2025 employee limit: \\$23,500/yr (\\$31,000 if age 50+).** "
        "Return to your employer plan and fill it past the match all the way to the statutory cap."
    )
    tier += 1

    st.markdown(
        f"**{tier}. Taxable Brokerage — no contribution limit.** Deploy every remaining dollar of margin "
        "into low-cost, broad-market index ETFs. This is where surplus capital lives once the "
        "sheltered tiers above are full."
    )

    st.info(
        "**The Fiduciary Threshold.** Once you are maxing every tax-advantaged account above *every "
        "year* and building a large, complex taxable estate, you have crossed the Fiduciary Threshold. "
        "DIY optimization stops paying for itself here. Hand ongoing management to a **fee-only, "
        "fiduciary RIA** — flat or hourly fee, never a percentage of assets and never commissions. "
        "This is the one point where paying for advice is the mathematically correct move."
    )

    st.divider()
    st.subheader("Goal Trajectory Modeling")
    st.caption(
        "Capital without a target is wasted motion. Name the objective and the number. We project the "
        "timeline using your Guilt-Free Margin compounding at a conservative 7% annualized return."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.goal_name = st.text_input(
            "Target Objective", value=st.session_state.goal_name, placeholder="e.g. 20% House Down Payment"
        )
    with col2:
        st.session_state.goal_target = st.number_input(
            "Target Capital Required ($)", min_value=0.0, step=1000.0, value=st.session_state.goal_target
        )

    goal_target = st.session_state.goal_target or 0.0
    goal_name = (st.session_state.goal_name or "").strip()

    if margin <= 0:
        st.warning(
            "Your Guilt-Free Margin is zero or negative, so there is nothing to deploy yet. Return to "
            "the earlier stages and free up cash flow before modeling a trajectory."
        )
    elif goal_target > 0 and goal_name:
        monthly_rate = ANNUAL_RATE / 12.0

        # Future value of an annuity solved for the number of monthly contributions:
        #   FV = PMT * ((1 + r)^n - 1) / r  ->  n = ln(1 + FV*r/PMT) / ln(1 + r)
        n_months = math.ceil(
            math.log((goal_target * monthly_rate / margin) + 1.0) / math.log(1.0 + monthly_rate)
        )
        n_months = max(1, min(n_months, MAX_TRAJECTORY_MONTHS))

        years, rem_months = divmod(n_months, 12)
        if years and rem_months:
            time_str = f"{years} yr {rem_months} mo"
        elif years:
            time_str = f"{years} yr"
        else:
            time_str = f"{rem_months} mo"

        st.success(
            f"🎯 **Trajectory locked.** Investing your **\\${margin:,.2f}** monthly margin at 7% reaches "
            f"**\\${goal_target:,.2f}** for *{goal_name}* in **{time_str}**."
        )

        # Ordinary-annuity accumulation (contribution at period end) so the
        # plotted curve reaches the target on exactly the month reported above.
        timeline_data = []
        current_date = datetime.date.today()
        accumulated = 0.0
        for m in range(n_months + 1):
            if m > 0:
                accumulated = accumulated * (1.0 + monthly_rate) + margin
            timeline_data.append({
                "Date": current_date + pd.DateOffset(months=m),
                "Projected Capital ($)": min(accumulated, goal_target),
            })

        st.line_chart(pd.DataFrame(timeline_data).set_index("Date"))
    else:
        st.caption("Enter a target objective and a dollar amount above to model your compounding timeline.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("🔄 Restart Audit", on_click=reset)
