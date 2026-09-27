import streamlit as st
import pandas as pd
import datetime
import math
from views import _anchor

ANNUAL_RATE = 0.07
MAX_TRAJECTORY_MONTHS = 1200  # 100-year cap keeps the chart bounded.


def render(next_step, prev_step, reset, margin):
    st.header("Now — the fun part: building the thing you came here for")
    st.markdown(
        "The cleanup is done: free money captured, safety net funded, toxic debt handled. From here, the tone "
        "shifts from defense to offense. Below is the exact order to fill your buckets so that not a dollar of "
        f"growth is wasted on taxes. Fill each one to its limit before moving to the next — that's the whole trick."
    )
    st.caption("You're already grabbing your full 401(k) match from earlier — that's free money and it always comes first, before everything below.")

    has_hsa = st.session_state.hdhp_status == "Yes, I'm on an HDHP"
    tier = 1

    if has_hsa:
        st.markdown(
            f"**{tier}. Your HSA — 2025 limit: \\$4,300 (self) / \\$8,550 (family), +\\$1,000 if you're 55+.** The only "
            "triple-tax-free account there is. Invest it in a simple broad-market fund and, if you can, don't spend "
            "it on today's medical bills — let it grow."
        )
        tier += 1

    st.markdown(
        f"**{tier}. Roth IRA — 2025 limit: \\$7,000/yr (\\$8,000 if you're 50+).** Grows and comes out completely "
        "tax-free in retirement. Low-cost, broad-market index funds are all you need."
    )
    tier += 1
    st.markdown(
        f"**{tier}. Back to your 401(k) — 2025 limit: \\$23,500/yr (\\$31,000 if you're 50+).** Past the match now, "
        "fill it the rest of the way to the cap."
    )
    tier += 1
    st.markdown(
        f"**{tier}. Regular brokerage account — no limit.** Once the tax-advantaged buckets are full, everything "
        "else goes here, in the same simple index funds. This is where real surplus lives."
    )

    st.info(
        "**A quiet milestone worth naming.** Once you're maxing every account above *every year* and building a "
        "sizable taxable account on top, you've reached what we'd call the Fiduciary Threshold. At that point, "
        "doing it yourself stops adding much, and it's worth handing the ongoing work to a **fee-only, fiduciary "
        "advisor** — flat or hourly fee, never a % of your assets, never commissions. That's the one time paying "
        "for advice is the mathematically right call. It's a good problem to have — and it's on this path."
    )

    st.divider()
    st.subheader("Your timeline to what you actually came for")
    st.markdown(
        f"Let's make **{_anchor.anchor_phrase()}** concrete. Put a number on it, and we'll project how long it "
        "takes using your spare cash and a realistic **7%** average yearly return — the kind index investors have "
        "historically earned over the long run."
    )

    col1, col2 = st.columns(2)
    with col1:
        default_goal = st.session_state.goal_name or _anchor.anchor_label()
        st.session_state.goal_name = st.text_input(
            "What are you aiming at?", value=default_goal, placeholder="e.g. A house down payment, or $1M invested"
        )
    with col2:
        st.session_state.goal_target = st.number_input(
            "How much will it take? ($)", min_value=0.0, step=1000.0, value=st.session_state.goal_target
        )

    goal_target = st.session_state.goal_target or 0.0
    goal_name = (st.session_state.goal_name or "").strip()

    if margin <= 0:
        st.warning(
            "Right now there's no spare monthly cash to invest yet — and that's okay. Head back a few steps to "
            "free some up, and this projection will light up the moment you do."
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
            f"🎯 **Here's your path.** Putting your **\\${margin:,.2f}/mo** to work at 7% gets you to "
            f"**\\${goal_target:,.2f}** for *{goal_name}* in about **{time_str}**. Not someday — a real date you can plan around."
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
        st.caption("Automate the monthly transfer and this basically runs itself. That's the whole point: a clear, automatic, mathematically sound path — so you can stop worrying and go live your life.")
    else:
        st.caption("Name your goal and put a number on it above, and I'll map the exact timeline for you.")

    st.divider()
    c1, c2 = st.columns([1, 5])
    c1.button("Back", on_click=prev_step)
    c2.button("🔄 Start over", on_click=reset)
