import streamlit as st
import pandas as pd
import plotly.express as px

from logic.cyber_ops import CyberOps
from logic.data_catalog import DataCatalog
from logic.service_desk import ServiceDesk
from logic.assistant import explain_queue


def command_center(db_path: str):
    ops = CyberOps(db_path)
    cat = DataCatalog(db_path)
    desk = ServiceDesk(db_path)

    tabs = st.tabs(["Security Queue", "Data Registry", "Service Desk", "Ops Assistant"])

    with tabs[0]:
        df = ops.frame()
        _security_view(df, ops)

    with tabs[1]:
        df = cat.frame()
        _data_view(df, cat)

    with tabs[2]:
        df = desk.frame()
        _it_view(df, desk)

    with tabs[3]:
        st.subheader("Ops Assistant")
        st.caption("Ask questions across queues.")

        q = st.text_area("Question", height=90)
        scope = st.selectbox("Context scope", ["Security Queue", "Data Registry", "Service Desk", "All"])

        ctx = ""
        if scope in ("Security Queue", "All"):
            ctx += _df_to_context("SECURITY", ops.frame())
        if scope in ("Data Registry", "All"):
            ctx += _df_to_context("DATA", cat.frame())
        if scope in ("Service Desk", "All"):
            ctx += _df_to_context("IT", desk.frame())

        if st.button("Generate guidance", type="primary"):
            if not q.strip():
                st.warning("Write a question first.")
            else:
                try:
                    st.write(explain_queue(q, ctx))
                except Exception as e:
                    st.error(str(e))



def _security_view(df: pd.DataFrame, ops: CyberOps):
    st.subheader("Security Queue")

    if df.empty:
        st.info("No security events found.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Open", int((df["state"] == "Open").sum()))
        k2.metric("In Progress", int((df["state"] == "In Progress").sum()))
        k3.metric("High/Critical", int(df["impact"].isin(["High", "Critical"]).sum()))
        k4.metric("Total", int(len(df)))

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            fig = px.histogram(df, x="impact", color="state", barmode="group")
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = px.pie(df, names="event_kind")
            st.plotly_chart(fig2, width="stretch")

        st.write("### Update status")
        key = st.selectbox("Event", df["event_key"].tolist(), key="sec_pick")
        new_state = st.selectbox("New state", ["Open", "In Progress", "Resolved", "Closed"], key="sec_state")
        if st.button("Apply update", key="sec_apply"):
            ops.update_state(key, new_state)
            st.success("Updated.")
            st.rerun()

        st.write("### Current queue")
        st.dataframe(df, use_container_width=True)

    st.write("### Create new security event")
    with st.form("sec_create", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            event_key = st.text_input("Event key (unique)", placeholder="SEC-999")
            event_kind = st.text_input("Event kind", placeholder="Phishing")
        with c2:
            impact = st.selectbox("Impact", ["Low", "Medium", "High", "Critical"])
            state = st.selectbox("State", ["Open", "In Progress", "Resolved", "Closed"])
        with c3:
            raised_at = st.text_input("Raised at (YYYY-MM-DD)", placeholder="2025-12-12")
            owner = st.text_input("Owner", placeholder="Analyst1")

        notes = st.text_area("Notes", height=80)

        if st.form_submit_button("Add event", type="primary"):
            if not (event_key.strip() and event_kind.strip() and raised_at.strip() and owner.strip()):
                st.warning("Fill event key, kind, raised date, and owner.")
            else:
                ops.add_event(
                    event_key=event_key.strip(),
                    event_kind=event_kind.strip(),
                    impact=impact,
                    state=state,
                    raised_at=raised_at.strip(),
                    owner=owner.strip(),
                    notes=notes.strip(),
                )
                st.success("Event added.")
                st.rerun()


def _data_view(df: pd.DataFrame, cat: DataCatalog):
    st.subheader("Data Registry")

    if df.empty:
        st.info("No data assets found.")
    else:
        k1, k2, k3 = st.columns(3)
        k1.metric("Assets", int(len(df)))
        k2.metric("Total size (MB)", float(df["size_mb"].sum()))
        k3.metric("Total rows", int(df["rows_est"].sum()))

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            fig = px.bar(df.sort_values("size_mb", ascending=False).head(8), x="asset_name", y="size_mb")
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = px.histogram(df, x="origin")
            st.plotly_chart(fig2, width="stretch")

        st.write("### Update steward")
        asset = st.selectbox("Asset", df["asset_name"].tolist(), key="asset_pick")
        steward = st.text_input("New steward", key="asset_steward")
        if st.button("Change steward", key="asset_apply"):
            if steward.strip():
                cat.change_steward(asset, steward.strip())
                st.success("Updated.")
                st.rerun()
            else:
                st.warning("Enter a steward name.")

        st.write("### Registry")
        st.dataframe(df, use_container_width=True)

    st.write("### Register new data asset")
    with st.form("asset_create", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            asset_name = st.text_input("Asset name (unique)")
            steward = st.text_input("Steward")
        with c2:
            origin = st.text_input("Origin system", placeholder="LMS / ERP / SIEM")
            size_mb = st.number_input("Size (MB)", min_value=0.0, value=100.0)
        with c3:
            rows_est = st.number_input("Rows estimate", min_value=0, value=1000)
            created_on = st.text_input("Created on (YYYY-MM-DD)", placeholder="2025-12-12")

        if st.form_submit_button("Add asset", type="primary"):
            if not (asset_name.strip() and steward.strip() and origin.strip() and created_on.strip()):
                st.warning("Fill asset name, steward, origin, and created date.")
            else:
                cat.add_asset(
                    asset_name=asset_name.strip(),
                    steward=steward.strip(),
                    origin=origin.strip(),
                    size_mb=float(size_mb),
                    rows_est=int(rows_est),
                    created_on=created_on.strip(),
                )
                st.success("Asset added.")
                st.rerun()


def _it_view(df: pd.DataFrame, desk: ServiceDesk):
    st.subheader("Service Desk")

    if df.empty:
        st.info("No IT requests found.")
    else:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Open", int((df["phase"] == "Open").sum()))
        k2.metric("In Progress", int((df["phase"] == "In Progress").sum()))
        k3.metric("Resolved", int((df["phase"] == "Resolved").sum()))
        k4.metric("Total", int(len(df)))

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            fig = px.histogram(df, x="urgency", color="phase", barmode="group")
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = px.pie(df, names="topic")
            st.plotly_chart(fig2, width="stretch")

        st.write("### Update phase")
        req = st.selectbox("Request", df["req_key"].tolist(), key="req_pick")
        phase = st.selectbox("New phase", ["Open", "In Progress", "Resolved", "Closed"], key="req_phase")
        if st.button("Apply phase change", key="req_apply"):
            desk.set_phase(req, phase)
            st.success("Updated.")
            st.rerun()

        st.write("### Requests")
        st.dataframe(df, use_container_width=True)

    st.write("### Log new IT request")
    with st.form("req_create", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            req_key = st.text_input("Request key (unique)", placeholder="REQ-4001")
            topic = st.text_input("Topic", placeholder="WiFi Coverage")
        with c2:
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Critical"])
            phase = st.selectbox("Phase", ["Open", "In Progress", "Resolved", "Closed"])
        with c3:
            opened_at = st.text_input("Opened at (YYYY-MM-DD)", placeholder="2025-12-12")
            assignee = st.text_input("Assignee", placeholder="DeskA")

        if st.form_submit_button("Add request", type="primary"):
            if not (req_key.strip() and topic.strip() and opened_at.strip() and assignee.strip()):
                st.warning("Fill request key, topic, opened date, and assignee.")
            else:
                desk.add_request(
                    req_key=req_key.strip(),
                    topic=topic.strip(),
                    urgency=urgency,
                    phase=phase,
                    opened_at=opened_at.strip(),
                    assignee=assignee.strip(),
                )
                st.success("Request added.")
                st.rerun()


def _df_to_context(title: str, df: pd.DataFrame) -> str:
    
    if df.empty:
        return f"\n[{title}] no rows\n"
    slim = df.head(30).to_dict(orient="records")
    return f"\n[{title}] {slim}\n"
    