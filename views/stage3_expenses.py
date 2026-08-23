import streamlit as st

def render(next_step, prev_step, margin):
    # Full-screen takeover when in a deficit
    if st.session_state.base_committed is not None and margin <= 0:
        committed_val = st.session_state.base_committed
        take_home_val = st.session_state.take_home or 0.0
        deficit_val = abs(margin)

        st.error("🚨 **CRITICAL DEFICIT: STOP THE BLEEDING**")
        st.markdown(
            f"Your committed monthly obligations (**\\${committed_val:,.2f}**) equal or exceed your take-home pay (**\\${take_home_val:,.2f}**).\n\n"
            f"You are operating at a monthly deficit of **\\${deficit_val:,.2f}**. You cannot build wealth or pay off debt on a negative foundation. You must adjust your numbers by playing defense, offense, or both."
        )
        
        col_exp, col_inc = st.columns(2)
        
        with col_exp:
            st.subheader("🛡️ Defense: Cut Expenses")
            st.markdown("""
            * **Audit Recurring Subscriptions:** Cancel streaming services, gym memberships, and unused app subscriptions.
            * **Negotiate Fixed Bills:** Call auto insurance providers for quotes, negotiate internet rates, or switch to a discount cell carrier.
            * **Groceries vs. Dining Out:** Cut takeout completely until cash flow is positive. Plan weekly meals around staples.
            * **Pause Discretionary Spending:** Freeze non-essential purchases (clothing, electronics, entertainment).
            """)
            
        with col_inc:
            st.subheader("⚔️ Offense: Increase Income")
            st.markdown("""
            * **Monetize Unused Assets:** Sell clutter, electronics, or furniture on Facebook Marketplace or OfferUp for immediate cash.
            * **Short-Term Cash Flow:** Pick up shifts, overtime, or temporary gig work (delivery, rideshare, task platforms).
            * **Freelance / Skill Monetization:** Offer immediate services based on your professional skillset.
            * **Career Renegotiation:** Schedule a review for a raise or begin interviewing for higher-paying positions.
            """)
            
        st.divider()
        st.subheader("Choose your next operational move:")
        st.caption("Select the action you took to fix the imbalance so the system can update your baseline numbers.")
        
        def go_to_income():
            st.session_state.step = 1

        def reset_expenses_only():
            st.session_state.base_committed = None

        btn_c1, btn_c2, btn_c3 = st.columns(3)
        
        btn_c1.button("📉 I Decreased My Expenses", on_click=reset_expenses_only, use_container_width=True)
        btn_c2.button("📈 I Increased My Income", on_click=go_to_income, use_container_width=True)
        btn_c3.button("⚡ I Did Both", on_click=go_to_income, use_container_width=True)

    else:
        # Standard input screen
        st.header("Step 3: Baseline Expenses")
        st.caption("What absolutely must leave your account every month to keep the lights on? **DO NOT include large, multi-month expenses here** (like annual car registration or Christmas). We will factor those in later. Only include strict monthly minimums (rent, groceries, utilities, minimum debt payments).")
        
        st.session_state.base_committed = st.number_input(
            "Monthly Baseline Committed Bills ($)", 
            min_value=0.0, 
            step=100.0, 
            value=st.session_state.base_committed
        )
        
        st.divider()
        c1, c2 = st.columns([1, 5])
        c1.button("Back", on_click=prev_step)
        
        if st.session_state.base_committed is not None and st.session_state.base_committed > 0:
            c2.button("Next", on_click=next_step, type="primary")
        else:
            c2.button("Enter your expenses to continue", disabled=True)
