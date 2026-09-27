import streamlit as st
from views import _anchor


def render(next_step, prev_step):
    st.title("One Small Leap")
    st.markdown(
        "Money isn't really about spreadsheets — it's about the life you're trying to build, and "
        "the stress you're trying to put down. So before we touch a single number, let's get honest "
        "about what you actually want. **Everything after this is in service of that.**"
    )

    st.divider()
    st.subheader("First — what are we really doing this for?")
    st.caption(
        "There's no wrong answer, and you can change it later. Pick whatever feels most true right now. "
        "We'll come back to it every time a decision gets hard."
    )

    options = list(_anchor.DRIVERS.keys())
    current = st.session_state.get("anchor_goal")
    idx = options.index(current) if current in options else 0
    st.session_state.anchor_goal = st.radio(
        "When you imagine money finally feeling *handled*, what's the feeling you're chasing?",
        options,
        index=idx,
    )

    st.session_state.anchor_detail = st.text_input(
        "Want to say it in your own words? (optional, but it makes this yours)",
        value=st.session_state.get("anchor_detail", ""),
        placeholder="e.g. A paid-off house and never dreading a bill again",
    )

    st.divider()
    st.subheader("And who's steering the ship?")
    st.caption("Managing money solo is a different game than managing it with a partner. No judgment either way.")
    house_options = ["Just me", "Me and a partner (shared finances)"]
    h_current = st.session_state.get("household")
    h_idx = house_options.index(h_current) if h_current in house_options else 0
    st.session_state.household = st.radio("Which fits you?", house_options, index=h_idx)

    st.divider()
    st.markdown(
        "That's the anchor. From here on out, I'm not here to judge your choices — I'm here to make the "
        "math work *for* the life you just described. Let's take the first small leap."
    )
    st.button("Let's begin →", on_click=next_step, type="primary")
