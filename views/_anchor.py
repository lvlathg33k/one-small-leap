"""Shared helpers for the user's emotional 'Rich Life' anchor.

The anchor is captured in Phase 1 and referenced throughout the app so that
every directive is framed as protecting what the user actually cares about,
rather than as a punishment.
"""
import streamlit as st

# Emotional drivers -> a natural phrase we can drop into a sentence.
DRIVERS = {
    "Security & peace of mind": "the security and peace of mind you're building toward",
    "Buying a home": "the home you're working toward",
    "Getting out of debt for good": "getting out from under this debt for good",
    "Freedom to walk away from a job": "the freedom to walk away on your own terms",
    "Providing for my family": "taking care of the people who count on you",
    "Retiring early / financial independence": "your early exit from work you *have* to do",
    "Just feeling in control for once": "finally feeling in control of your money",
}

DEFAULT_PHRASE = "your Rich Life"


def anchor_phrase(fallback=DEFAULT_PHRASE):
    """Return an in-sentence phrase for the user's chosen driver."""
    label = st.session_state.get("anchor_goal")
    if label in DRIVERS:
        return DRIVERS[label]
    return fallback


def anchor_label():
    """Return the raw driver label the user selected (or empty string)."""
    label = st.session_state.get("anchor_goal")
    return label if label in DRIVERS else ""


def sidebar_phrase():
    """What to pin in the sidebar as a persistent reminder of the 'why'."""
    detail = (st.session_state.get("anchor_detail") or "").strip()
    if detail:
        return detail
    return anchor_label()
