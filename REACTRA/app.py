"""REACTRA: Reaction-Aware Field Testing & Verifiable Evidence.

SIH Problem Statement: SIH26231 — Digital Companion for Field Drug Testing.
Authoritative Entry Point: streamlit run app.py
"""

from __future__ import annotations

import logging

import streamlit as st

from rectra.config import (
    PRIVATE_KEY_PATH,
    PUBLIC_KEY_PATH,
    RECTRA_DB_PATH,
    RECTRA_KEY_DIR,
    RECTRA_PROFILE_ID,
    RECTRA_PROFILE_VERSION,
)
from rectra.core.constants import (
    DISCLAIMER_LAB_REQUIRED,
    DISCLAIMER_PRESUMPTIVE,
    DISCLAIMER_SYNTHETIC_NOTE,
)
from rectra.core.logging_config import configure_logging
from rectra.database.connection import get_connection
from rectra.database.schema import create_tables
from rectra.profiles.loader import load_profile
from rectra.ui.pages import (
    render_demo_page,
    render_field_operator_workflow,
    render_home_page,
    render_referral_page,
    render_test_history_page,
)

# Initialize logging
configure_logging()
logger = logging.getLogger("reactra.app")

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="REACTRA — Field Test Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_runtime() -> dict[str, bool]:
    """Verify and initialize runtime resources (keys, database, profile)."""
    status = {"keys": False, "db": False, "profile": False}

    # 1. Key check & generation
    if not (PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists()):
        try:
            from scripts.generate_demo_keys import generate_keys

            generate_keys()
            status["keys"] = True
            logger.info("Generated development Ed25519 keypair at %s", RECTRA_KEY_DIR)
        except Exception as exc:
            logger.error("Failed to generate keys: %s", exc)
    else:
        status["keys"] = True

    # 2. Database check & creation
    try:
        conn = get_connection(RECTRA_DB_PATH)
        create_tables(conn)
        conn.close()
        status["db"] = True
    except Exception as exc:
        logger.error("Failed to initialize database at %s: %s", RECTRA_DB_PATH, exc)

    # 3. Assay profile check
    try:
        load_profile()
        status["profile"] = True
    except Exception as exc:
        logger.error("Failed to load default assay profile: %s", exc)

    return status


# Run first-run checks
init_status = initialize_runtime()

# Persistent header banner
HEADER_HTML = """
<div style="background-color: #1e293b; padding: 12px 20px; border-radius: 8px;
            margin-bottom: 20px; border-left: 5px solid #3b82f6;">
    <span style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">🔬 REACTRA</span>
    <span style="color: #94a3b8; margin-left: 10px;">
        | Reaction-Aware Field Testing & Verifiable Evidence
    </span>
    <span style="float: right; color: #fbbf24; font-size: 0.85rem; font-weight: 600;">
        SIH26231
    </span>
</div>
"""
st.markdown(HEADER_HTML, unsafe_allow_html=True)

# Sidebar Mode and Navigation
st.sidebar.title("REACTRA")
mode = st.sidebar.radio(
    "Operating Mode:",
    ["👮 Field Operator Mode", "🛠️ Validation & QA Mode"],
    index=0,
)

if mode == "👮 Field Operator Mode":
    pages = [
        "HOME",
        "START FIELD TEST",
        "TEST HISTORY ARCHIVE",
        "LAB REFERRAL PACKETS",
    ]
else:
    pages = [
        "VALIDATION & QA",
        "HOME",
    ]

# Handle programmatic page navigation
if "nav_target" in st.session_state and st.session_state["nav_target"] in pages:
    current_page_idx = pages.index(st.session_state["nav_target"])
    del st.session_state["nav_target"]
else:
    current_page_idx = 0

selected_page = st.sidebar.radio("Navigate:", pages, index=current_page_idx)

# Sidebar Runtime Status Card
with st.sidebar.expander("System Health", expanded=False):
    st.write(f"🔑 Keys: {'✅ Ready (Ed25519)' if init_status['keys'] else '❌ Error'}")
    st.write(f"💾 Database: {'✅ Connected' if init_status['db'] else '❌ Error'}")
    st.write(f"📋 Profile: {'✅ Loaded' if init_status['profile'] else '❌ Missing'}")
    st.caption(f"Profile: `{RECTRA_PROFILE_ID} v{RECTRA_PROFILE_VERSION}`")

# Global Disclaimer in Sidebar
st.sidebar.markdown("---")
st.sidebar.caption(
    f"**Notice:** {DISCLAIMER_PRESUMPTIVE}. {DISCLAIMER_LAB_REQUIRED}\n\n"
    f"{DISCLAIMER_SYNTHETIC_NOTE}"
)

# Page Routing
if selected_page == "HOME":
    render_home_page()
elif selected_page == "START FIELD TEST":
    render_field_operator_workflow()
elif selected_page == "TEST HISTORY ARCHIVE":
    render_test_history_page()
elif selected_page == "LAB REFERRAL PACKETS":
    render_referral_page()
elif selected_page == "VALIDATION & QA":
    render_demo_page()
