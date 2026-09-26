"""
Streamlit frontend for ResolveAI.

Run it from the ResolveAI/ project root with:
    streamlit run frontend/dashboard.py

Make sure the backend is also running (in a separate terminal):
    uvicorn backend.api:app --reload

This app only talks to the backend for submitting NEW complaints
(POST /analyze). For the dashboard and history pages, it reads
data/complaints.csv directly with pandas — no extra API endpoints
needed, which keeps things simple.
"""

import os
import sys

import pandas as pd
import requests
import streamlit as st

# Make sure "backend" and "ai" are importable when Streamlit runs this
# file directly (streamlit run frontend/dashboard.py).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.processor import load_complaints  # noqa: E402

API_URL = os.getenv("RESOLVEAI_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="ResolveAI", page_icon="🛠️", layout="wide")


# ----------------------------- helpers -----------------------------

def call_analyze_api(customer_name: str, email: str, complaint: str) -> dict:
    """Calls the backend's POST /analyze endpoint. Raises on failure."""
    response = requests.post(
        f"{API_URL}/analyze",
        json={"customer_name": customer_name, "email": email, "complaint": complaint},
        timeout=60,
    )
    if response.status_code != 200:
        # FastAPI puts the readable error message in "detail"
        detail = response.json().get("detail", response.text)
        raise RuntimeError(detail)
    return response.json()


def check_backend_health() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ----------------------------- sidebar nav -----------------------------

st.sidebar.title("🛠️ ResolveAI")
page = st.sidebar.radio("Go to", ["New Complaint", "Dashboard", "Complaint History"])

if check_backend_health():
    st.sidebar.success("Backend: connected")
else:
    st.sidebar.error("Backend: not reachable\n\nStart it with:\nuvicorn backend.api:app --reload")


# ----------------------------- page: new complaint -----------------------------

if page == "New Complaint":
    st.title("Submit a New Complaint")
    st.write("Enter the customer's details and complaint. ResolveAI will analyze it automatically.")

    with st.form("complaint_form", clear_on_submit=False):
        customer_name = st.text_input("Customer name")
        email = st.text_input("Email")
        complaint = st.text_area("Complaint", height=150)
        submitted = st.form_submit_button("Analyze Complaint")

    if submitted:
        if not customer_name.strip() or not email.strip() or not complaint.strip():
            st.warning("Please fill in all three fields before submitting.")
        else:
            with st.spinner("Analyzing complaint..."):
                try:
                    result = call_analyze_api(customer_name, email, complaint)
                except RuntimeError as exc:
                    st.error(f"Analysis failed: {exc}")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Could not reach the backend API: {exc}")
                else:
                    st.success("Complaint analyzed and saved.")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Category", result["category"])
                    col2.metric("Urgency", result["urgency"])
                    col3.metric("Department", result["department"])

                    st.subheader("Summary")
                    st.write(result["summary"])

                    st.subheader("Suggested Action")
                    st.write(result["suggested_action"])

                    st.subheader("Suggested Customer Reply")
                    st.info(result["customer_reply"])


# ----------------------------- page: dashboard -----------------------------

elif page == "Dashboard":
    st.title("Dashboard")

    df = load_complaints()

    if df.empty:
        st.info("No complaints recorded yet. Submit one on the 'New Complaint' page.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Complaints", len(df))
        col2.metric("High Urgency", int((df["urgency"] == "High").sum()))
        col3.metric("Departments Involved", df["department"].nunique())

        st.subheader("Complaints by Category")
        st.bar_chart(df["category"].value_counts())

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Complaints by Urgency")
            urgency_order = ["Low", "Medium", "High"]
            urgency_counts = df["urgency"].value_counts().reindex(urgency_order, fill_value=0)
            st.bar_chart(urgency_counts)

        with col_b:
            st.subheader("Complaints by Department")
            st.bar_chart(df["department"].value_counts())


# ----------------------------- page: complaint history -----------------------------

elif page == "Complaint History":
    st.title("Complaint History")

    df = load_complaints()

    if df.empty:
        st.info("No complaints recorded yet. Submit one on the 'New Complaint' page.")
    else:
        with st.expander("Search and Filters", expanded=True):
            search_text = st.text_input("Search (name, email, or complaint text)")

            col1, col2 = st.columns(2)
            with col1:
                category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
                category_filter = st.selectbox("Category", category_options)
            with col2:
                urgency_options = ["All", "Low", "Medium", "High"]
                urgency_filter = st.selectbox("Urgency", urgency_options)

        filtered = df.copy()

        if search_text.strip():
            mask = (
                filtered["customer_name"].str.contains(search_text, case=False, na=False)
                | filtered["email"].str.contains(search_text, case=False, na=False)
                | filtered["complaint"].str.contains(search_text, case=False, na=False)
            )
            filtered = filtered[mask]

        if category_filter != "All":
            filtered = filtered[filtered["category"] == category_filter]

        if urgency_filter != "All":
            filtered = filtered[filtered["urgency"] == urgency_filter]

        filtered = filtered.sort_values("timestamp", ascending=False)

        st.write(f"Showing {len(filtered)} of {len(df)} complaints")
        st.dataframe(
            filtered[[
                "timestamp", "customer_name", "email", "category",
                "urgency", "department", "summary",
            ]],
            use_container_width=True,
        )

        with st.expander("View full details for a complaint"):
            if not filtered.empty:
                selected_id = st.selectbox(
                    "Select a complaint (by customer name + timestamp)",
                    filtered.index,
                    format_func=lambda i: f"{filtered.loc[i, 'customer_name']} — {filtered.loc[i, 'timestamp']}",
                )
                row = filtered.loc[selected_id]
                st.write("**Complaint:**", row["complaint"])
                st.write("**Suggested Action:**", row["suggested_action"])
                st.write("**Customer Reply:**", row["customer_reply"])
