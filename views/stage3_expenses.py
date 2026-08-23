import streamlit as st

def render(next_step, prev_step, margin):
    st.header("Step 3: Baseline Expenses")
    st.caption("What absolutely must leave your account every month to keep the lights on? **DO NOT include large, multi-month expenses here** (like annual car registration or Christmas). We will factor those in later. Only include strict monthly minimums (rent, groceries, utilities, minimum debt payments).")
    
    val = st.number_input(
        "Monthly Baseline Committed Bills ($)", 
        min_value=0.0, 
        step=100.0, 
        value=st.session_state.base_committed if st.session_state.base_committed is not None else 0.0
    )
    
    # Update state immediately from the current widget value
    st.session_state.base_committed = val
    take_home_val = st.session_state.take_home or 0.0
    current_margin = take_home_val - val

    st.divider()

    # DEFICIT HARD-STOP: Triggered whenever committed >= take_home and committed > 0
    if val > 0 and current_margin <= 0:
        deficit_val = abs(current_margin)
        st.error("🚨 **CRITICAL DEFICIT: PAUSE AND EXECUTE IN REAL LIFE**")
        st.markdown(
            f"Your committed monthly bills (**\\${val:,.2f}**) exceed your take-home pay (**\\${take_home_val:,.2f}**) "
            f"by **\\${deficit_val:,.2f}** every single month.\n\n"
            "**Do not rush past this screen.** You cannot mathematically build wealth or eliminate debt while cash flow is negative. "
            "Fixing this gap is not an in-app toggle—it requires real-world time, discipline, and execution."
        )
        
        col_exp, col_inc = st.columns(2)
        
        with col_exp:
            st.subheader("🛡️ Lever 1: Cut Fixed Overhead")
            st.markdown("""
            * **Immediate Subscriptions:** Cancel unused streaming, gym, and recurring software memberships today.
            * **Shop Fixed Services:** Get competitive quotes for car insurance, home/renters insurance, and home internet.
            * **Food Spending:** Eliminate restaurant meals and takeout until cash flow is positive.
            * **Discretionary Freeze:** Pause non-essential apparel, gear, and lifestyle purchases entirely.
            """)
            
        with col_inc:
            st.subheader("⚔️ Lever 2: Increase Gross Cash Flow")
            st.markdown("""
            * **Quick Asset Liquidation:** Sell unused electronics, tools, or furniture on local marketplaces for fast cash.
            * **Overtime / Extra Shifts:** Pick up additional hours at your current role if available.
            * **Short-Term Gig Work:** Deploy weekend or evening hours to rideshare, delivery, or local task contracts.
            * **Career Positioning:** Map out a structured plan for your next promotion or target higher-paying openings.
            """)
            
        st.divider()
        st.subheader("Step away from the screen.")
        st.markdown("""
        1. **Bookmark this URL.**
        2. Close this tab and execute at least **one defense** and **one offense** action in your actual life.
        3. Return only after your real monthly cash flow has shifted into positive territory.
        """)

        def reset_to_step_1():
            st.session_state.step = 1
            st.session_state.base_committed = None

        st.button("🔄 I Have Executed Changes in Real Life (Update Numbers)", on_click=reset_to_step_1, type="primary")

    else:
        # Standard navigation buttons when margin is positive
        c1, c2 = st.columns([1, 5])
        c1.button("Back", on_click=prev_step)
        
        if val > 0:
            c2.button("Next", on_click=next_step, type="primary")
        else:
            c2.button("Enter your expenses to continue", disabled=True)
