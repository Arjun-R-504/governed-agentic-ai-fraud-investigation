
import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Fraud Investigation Dashboard",
    page_icon="🔎",
    layout="wide"
)

# We will add your n8n webhook URL here later.
N8N_WEBHOOK_URL = "PASTE_N8N_WEBHOOK_URL_HERE"

st.title("🔎 Banking Fraud Investigation")
st.caption("Governed Agentic AI for Banking Fraud Investigation and Response")

st.info(
    "Student prototype using synthetic data only. "
    "All risk assessments and recommendations require human review."
)

cases = {
    "FR-1001 — Routine review": {
        "case_id": "FR-1001",
        "customer_id": "CUST-SYN-001",
        "transaction_amount": 75000,
        "usual_amount": 12000,
        "channel": "Mobile banking",
        "device": "Known device",
        "location": "Familiar location",
        "failed_logins": 0,
        "previous_alerts": 0,
        "verification_status": "Confirmed legitimate",
        "evidence_status": "Complete",
        "scenario": "Normal"
    },
    "FR-1002 — Additional verification": {
        "case_id": "FR-1002",
        "customer_id": "CUST-SYN-002",
        "transaction_amount": 125000,
        "usual_amount": 18000,
        "channel": "Web banking",
        "device": "New device",
        "location": "Unfamiliar location",
        "failed_logins": 1,
        "previous_alerts": 0,
        "verification_status": (
            "Verification record suggests legitimate; "
            "not independently confirmed"
        ),
        "evidence_status": "Partial",
        "scenario": "Ambiguous"
    },
    "FR-1003 — Urgent human escalation": {
        "case_id": "FR-1003",
        "customer_id": "CUST-SYN-003",
        "transaction_amount": 240000,
        "usual_amount": 15000,
        "channel": "Mobile banking",
        "device": "New device",
        "location": "Unfamiliar location",
        "failed_logins": 5,
        "previous_alerts": 3,
        "verification_status": "Not available",
        "evidence_status": "Incomplete",
        "scenario": "High-risk"
    }
}

st.subheader("Select a synthetic fraud case")

selected_case = st.selectbox(
    "Choose a test case",
    list(cases.keys())
)

case = cases[selected_case]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Transaction amount", f"₹{case['transaction_amount']:,}")
    st.write("**Case ID:**", case["case_id"])
    st.write("**Customer:**", case["customer_id"])

with col2:
    st.write("**Channel:**", case["channel"])
    st.write("**Device:**", case["device"])
    st.write("**Location:**", case["location"])

with col3:
    st.write("**Verification:**", case["verification_status"])
    st.write("**Evidence:**", case["evidence_status"])
    st.write("**Scenario:**", case["scenario"])

st.divider()

if st.button("Run Investigation", type="primary"):
    if N8N_WEBHOOK_URL == "PASTE_N8N_WEBHOOK_URL_HERE":
        st.warning(
            "The dashboard design is ready. "
            "We still need to connect it to your n8n workflow."
        )
    else:
        try:
            with st.spinner("Sending case to the investigation workflow..."):
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json=case,
                    timeout=60
                )

            response.raise_for_status()

            st.success("Workflow response received.")
            try:
                st.json(response.json())
            except ValueError:
                st.write(response.text)

            st.warning(
                "This is decision support only. "
                "A human investigator must make the final decision."
            )

        except requests.RequestException as error:
            st.error(f"Could not connect to the workflow: {error}")

with st.expander("View synthetic case data"):
    st.json(case)

st.caption(
    "No real customer data is used. "
    "The prototype does not freeze accounts or block transactions."
)
