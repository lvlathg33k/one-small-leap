import streamlit as st
from views import _anchor


def render(next_step, prev_step, margin):
    st.header("What does it cost to keep your life running?")
    st.markdown(
        f"To get you to **{_anchor.anchor_phrase()}**, we need an honest picture of what leaves your account "
        "every month no matter what. I mean the true non-negotiables: **rent or mortgage, utilities, groceries, "
        "insurance, transportation, and the minimum payments on your debts.**"
    )
    st.caption(
        "Leave out the big once-a-year stuff (car registration, holidays, that annual subscription) — those "
        "ambush expenses get their own step later, so you don't have to hold them in your head right now."
    )

    val = st.number_input(
        "Roughly what has to leave your account every month, just to keep the lights on?",
        min_value=0.0,
        step=100.0,
        value=st.session_state.base_committed if st.session_state.base_committed is not None else 0.0,
    )

    # Update state immediately from the current widget value
    st.session_state.base_committed = val
    take_home_val = st.session_state.take_home or 0.0
    current_margin = take_home_val - val

    st.divider()

    # DEFICIT HARD-STOP: Triggered whenever committed >= take_home and committed > 0
    if val > 0 and current_margin <= 0:
        deficit_val = abs(current_margin)
        st.subheader("Okay — let's slow down together for a minute.")
        st.markdown(
            f"Right now, the essentials (**\\${val:,.2f}**) are costing more than what comes in "
            f"(**\\${take_home_val:,.2f}**) — a gap of about **\\${deficit_val:,.2f}** every month. "
            "If you've been feeling a low hum of stress about money, *this* is the math behind that feeling. "
            "It is real, and it is not a character flaw. A huge number of people are living inside this exact gap."
        )
        st.markdown(
            f"Here's the hard truth, said gently: we can't invest or budget our way to **{_anchor.anchor_phrase()}** "
            "while more goes out than comes in each month. So before we go further, we close this gap in real life. "
            "There are only two levers, and you don't need both at once — one solid move is a win."
        )

        col_exp, col_inc = st.columns(2)
        with col_exp:
            st.subheader("🛡️ Lever 1: Lower what goes out")
            st.markdown("""
            * **Subscriptions:** Cancel the streaming / gym / app memberships you forgot you had. Start today.
            * **Shop your fixed bills:** Get fresh quotes on car, home, or renters insurance and your internet — a 20-minute call can cut a bill for good.
            * **Food:** Pause restaurants and takeout for now — it's the fastest lever most people have.
            * **Discretionary freeze:** Put non-essential shopping on hold until the gap closes. This is temporary, not forever.
            """)
        with col_inc:
            st.subheader("⚔️ Lever 2: Bring more in")
            st.markdown("""
            * **Sell what you're not using:** Electronics, tools, furniture — quick cash from stuff you won't miss.
            * **Extra hours:** Overtime or an extra shift at your current job, if that's available to you.
            * **Short-term gig work:** A few evening or weekend hours (delivery, rideshare, tasks) to bridge the gap.
            * **The bigger play:** Sketch a plan toward a raise or a higher-paying role — the real long-term fix.
            """)

        st.divider()
        st.subheader("Your one next step")
        st.markdown("""
        1. **Bookmark this page** so it's easy to come back to.
        2. Step away and take **one** action — one from either column counts.
        3. Come back when your monthly numbers have shifted, and we'll pick right back up.
        """)
        st.caption("This isn't a punishment — it's the one thing standing between you and everything we're about to build. You've got this.")

        def reset_to_step_1():
            st.session_state.step = 1
            st.session_state.base_committed = None

        st.button("I made a change in real life — let's update the numbers", on_click=reset_to_step_1, type="primary")

    else:
        if val > 0:
            st.success(
                f"Good — you've got about **\\${current_margin:,.2f}** left over each month after the essentials. "
                "That leftover is the engine we'll point straight at your goal. Let's keep going."
            )
        c1, c2 = st.columns([1, 5])
        c1.button("Back", on_click=prev_step)
        if val > 0:
            c2.button("Next", on_click=next_step, type="primary")
        else:
            c2.button("Add your monthly essentials to continue", disabled=True)
