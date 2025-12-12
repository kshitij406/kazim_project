import streamlit as st
from config import CFG
from core.bootstrap import ensure_schema
from logic.accounts import Accounts
from ui.layout import app_shell
from ui.screens import command_center

def main():
    app_shell("Ops Command Center", "Unified security, data, and IT operations view")

    ensure_schema(CFG.db_path)

    with st.sidebar:
        st.markdown("### Session")

        if "actor" not in st.session_state:
            st.markdown("### Sign in")
            handle = st.text_input("Handle")
            pwd = st.text_input("Password", type="password")
            if st.button("Sign in", type="primary"):
                acct = Accounts(CFG.db_path)
                user = acct.authenticate(handle.strip(), pwd)
                if user:
                    st.session_state["actor"] = user
                    st.success("Signed in.")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        else:
            u = st.session_state["actor"]
            st.write(f"Signed in as `{u['handle']}`")
            st.caption(f"Access: {u['access_level']}")
            if st.button("Sign out"):
                st.session_state.pop("actor")
                st.rerun()

    if "actor" not in st.session_state:
        st.info("Seed data by running: `python -m core.bootstrap` then sign in.")
        st.caption("Default demo login (after seeding): admin / admin123")
        return

    command_center(CFG.db_path)

if __name__ == "__main__":
    main()
