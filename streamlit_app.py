import json
from datetime import datetime

import requests
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sentinel | Fraud Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. SECURE N8N CONFIGURATION
#    The webhook URL must be stored in Streamlit Secrets,
#    never hardcoded into this public GitHub file.
# ============================================================

try:
    N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL", "").strip()
except Exception:
    N8N_WEBHOOK_URL = ""


# ============================================================
# 3. SYNTHETIC FRAUD CASES
# ============================================================

CASES = {
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
        "scenario": "Normal",
        "case_notes": (
            "The transaction is larger than usual, but the device, "
            "location and verification record are familiar."
        ),
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
        "scenario": "Ambiguous",
        "case_notes": (
            "Unusual device and location indicators conflict with "
            "a verification record that has not been independently confirmed."
        ),
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
        "scenario": "High-risk",
        "case_notes": (
            "Multiple unusual indicators are present, previous suspicious "
            "alerts exist, and supporting evidence is incomplete."
        ),
    },
}


# ============================================================
# 4. SESSION STATE
# ============================================================

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_case_id" not in st.session_state:
    st.session_state.last_case_id = None

if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = None


# ============================================================
# 5. VISUAL DESIGN
# ============================================================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --navy: #101b35;
        --navy-light: #1b2a4a;
        --teal: #11b8a6;
        --teal-light: #e6faf6;
        --muted: #718096;
        --border: #e4eaf2;
        --surface: #ffffff;
        --background: #f4f7fb;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(17, 184, 166, 0.07),
                transparent 25%
            ),
            var(--background);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: #101b35;
        border-right: 1px solid #263553;
    }

    [data-testid="stSidebar"] * {
        color: #e8eef8;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #b7c5db;
    }

    .brand-label {
        color: #11b8a6;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero {
        background: linear-gradient(120deg, #101b35 0%, #1c3154 75%, #175d68 130%);
        border: 1px solid #263c5c;
        border-radius: 22px;
        padding: 30px 32px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(16, 27, 53, 0.12);
    }

    .hero-kicker {
        color: #72e4d6;
        text-transform: uppercase;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .hero h1 {
        font-family: 'Manrope', sans-serif;
        font-size: clamp(28px, 3.2vw, 42px);
        font-weight: 800;
        line-height: 1.15;
        color: #ffffff;
        margin: 0 0 12px 0;
    }

    .hero p {
        color: #d0dced;
        font-size: 14px;
        line-height: 1.7;
        margin: 0;
        max-width: 800px;
    }

    .hero-chip {
        display: inline-block;
        margin-top: 18px;
        margin-right: 8px;
        padding: 7px 11px;
        border-radius: 100px;
        border: 1px solid #3d5875;
        background: rgba(255,255,255,0.07);
        color: #e8f5ff;
        font-size: 11px;
        font-weight: 700;
    }

    .section-heading {
        font-family: 'Manrope', sans-serif;
        color: #14213d;
        font-size: 20px;
        font-weight: 800;
        margin: 18px 0 4px 0;
    }

    .section-subtitle {
        color: #718096;
        font-size: 13px;
        margin-bottom: 15px;
    }

    .info-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 18px;
        min-height: 105px;
        box-shadow: 0 4px 14px rgba(16, 27, 53, 0.025);
    }

    .info-label {
        color: #718096;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        margin-bottom: 9px;
    }

    .info-value {
        color: #14213d;
        font-family: 'Manrope', sans-serif;
        font-size: 23px;
        font-weight: 800;
        line-height: 1.25;
        overflow-wrap: anywhere;
    }

    .info-detail {
        color: #8492a6;
        font-size: 11px;
        margin-top: 7px;
        line-height: 1.5;
    }

    .status-pill {
        display: inline-block;
        border-radius: 100px;
        padding: 6px 10px;
        font-size: 11px;
        font-weight: 800;
        background: #e9f2ff;
        color: #2858a5;
    }

    .governance-box {
        background: #effbf8;
        border: 1px solid #c8eee5;
        border-left: 4px solid #11b8a6;
        border-radius: 12px;
        padding: 16px 18px;
        color: #245c55;
        font-size: 13px;
        line-height: 1.65;
        margin: 12px 0 18px 0;
    }

    .governance-box strong {
        color: #124c45;
    }

    .case-note {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 15px 17px;
        color: #526176;
        font-size: 13px;
        line-height: 1.7;
        margin: 10px 0 18px 0;
    }

    .workflow-step {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 13px 14px;
        text-align: center;
        min-height: 105px;
    }

    .workflow-number {
        color: #11a896;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        margin-bottom: 7px;
    }

    .workflow-title {
        color: #182642;
        font-size: 12px;
        font-weight: 800;
        line-height: 1.45;
    }

    .workflow-detail {
        color: #8492a6;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 6px;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #0b9f92, #12b8a6);
        color: white;
        border: 0;
        border-radius: 10px;
        padding: 0.7rem 1.1rem;
        font-weight: 800;
        box-shadow: 0 5px 13px rgba(17, 184, 166, 0.18);
    }

    div.stButton > button[kind="primary"]:hover {
        background: #087f75;
        color: white;
        border: 0;
    }

    div.stButton > button {
        border-radius: 9px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        padding: 16px 18px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #718096;
        font-size: 12px;
    }

    div[data-testid="stMetricValue"] {
        color: #14213d;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        background: white;
    }

    .footer {
        text-align: center;
        color: #8794a7;
        font-size: 11px;
        padding: 22px 0 0 0;
        line-height: 1.7;
    }

    hr {
        border-color: #e4eaf2;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 22px 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 12px 0 18px 0;">
            <div style="font-size: 28px; font-weight: 800; color: white;">
                ◈ SENTINEL
            </div>
            <div style="color: #8fa5c3; font-size: 11px; letter-spacing: 1.5px;">
                FRAUD INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("**PROJECT NAVIGATION**")
    st.markdown("🔎  Fraud investigation")
    st.markdown("🧾  Evidence review")
    st.markdown("🛡️  Governance controls")

    st.markdown("---")
    st.markdown("**ENVIRONMENT**")

    st.markdown(
        '<span class="status-pill">SYNTHETIC DATA ONLY</span>',
        unsafe_allow_html=True,
    )

    st.write("")
    st.caption("Educational proof of concept")
    st.caption("No live banking systems connected.")

    st.markdown("---")
    st.markdown("**HUMAN OVERSIGHT**")
    st.markdown(
        """
        - Human investigator retains final authority.
        - Missing evidence must remain visible.
        - No automatic account freeze.
        - No automatic transaction blocking.
        """
    )


# ============================================================
# 7. HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Governed Agentic AI · Banking Operations</div>
        <h1>Fraud Investigation<br>Command Centre</h1>
        <p>
            A human-supervised decision-support prototype that organises
            suspicious transaction information, highlights evidence gaps,
            supports risk assessment and routes cases for appropriate review.
        </p>
        <span class="hero-chip">◈ Synthetic cases</span>
        <span class="hero-chip">◈ Evidence-aware</span>
        <span class="hero-chip">◈ Human-in-the-loop</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 8. OVERVIEW METRICS
# ============================================================

st.markdown(
    '<div class="section-heading">Investigation overview</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Explore three controlled scenarios before running an investigation.</div>',
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)

overview_metrics = [
    ("Test scenarios", "03", "Normal, ambiguous and high-risk"),
    ("Data environment", "Synthetic", "No real customer records"),
    ("Decision authority", "Human", "Final decision remains with investigator"),
    ("Automation", "n8n", "Workflow orchestration"),
]

for col, (label, value, detail) in zip(metric_cols, overview_metrics):
    with col:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">{label}</div>
                <div class="info-value">{value}</div>
                <div class="info-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 9. CASE SELECTION
# ============================================================

st.markdown(
    '<div class="section-heading">Select a fraud alert</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Each case contains fictional transaction and evidence information.</div>',
    unsafe_allow_html=True,
)

selected_case_name = st.selectbox(
    "Choose a test scenario",
    list(CASES.keys()),
)

case = CASES[selected_case_name]

st.markdown(
    f"""
    <div class="case-note">
        <strong>Case context:</strong> {case["case_notes"]}
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 10. TRANSACTION AND CUSTOMER CONTEXT
# ============================================================

st.markdown(
    '<div class="section-heading">Case intelligence</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">Transaction amount</div>
            <div class="info-value">₹{case["transaction_amount"]:,}</div>
            <div class="info-detail">
                Usual transaction: ₹{case["usual_amount"]:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("**Case ID:**", case["case_id"])
    st.write("**Synthetic customer:**", case["customer_id"])

with col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Access context</div>
            <div class="info-value" style="font-size: 18px;">Transaction signals</div>
            <div class="info-detail">
                Channel, device, location and login activity
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("**Channel:**", case["channel"])
    st.write("**Device:**", case["device"])
    st.write("**Location:**", case["location"])

with col3:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Evidence context</div>
            <div class="info-value" style="font-size: 18px;">Verification status</div>
            <div class="info-detail">
                Evidence completeness and prior alerts
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("**Verification:**", case["verification_status"])
    st.write("**Evidence:**", case["evidence_status"])
    st.write("**Previous suspicious alerts:**", case["previous_alerts"])
    st.write("**Failed logins:**", case["failed_logins"])

st.divider()


# ============================================================
# 11. ILLUSTRATIVE WORKFLOW
# ============================================================

st.markdown(
    '<div class="section-heading">Governed investigation pathway</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Logical roles represented by the n8n workflow. These steps do not independently make final fraud decisions.</div>',
    unsafe_allow_html=True,
)

workflow_cols = st.columns(5)

workflow_steps = [
    ("01", "Alert intake", "Receive synthetic case"),
    ("02", "Transaction triage", "Identify unusual signals"),
    ("03", "Evidence review", "Find gaps and conflicts"),
    ("04", "Risk assessment", "Apply illustrative rules"),
    ("05", "Human review", "Route for investigator action"),
]

for col, (number, title, detail) in zip(workflow_cols, workflow_steps):
    with col:
        st.markdown(
            f"""
            <div class="workflow-step">
                <div class="workflow-number">STAGE {number}</div>
                <div class="workflow-title">{title}</div>
                <div class="workflow-detail">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="governance-box">
        <strong>Governance rule:</strong> The workflow provides decision support.
        It must not independently determine that fraud has occurred, freeze an
        account, or block a transaction. Missing or conflicting evidence should
        be surfaced for a human investigator.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 12. INVESTIGATION ACTION
# ============================================================

st.markdown(
    '<div class="section-heading">Run investigation</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Send the selected synthetic case to the published n8n Production Webhook.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1, 2])

with left:
    run_investigation = st.button(
        "🔎  Run Investigation",
        type="primary",
        use_container_width=True,
    )

with right:
    st.caption(
        "Only fictional case information is sent. The response depends on "
        "how the n8n workflow is configured to process and return the request."
    )


# ============================================================
# 13. SEND CASE TO N8N
# ============================================================

if run_investigation:
    if not N8N_WEBHOOK_URL:
        st.error(
            "The n8n URL is not configured yet. Add N8N_WEBHOOK_URL "
            "to Streamlit Secrets before running an investigation."
        )

    elif not N8N_WEBHOOK_URL.startswith("https://"):
        st.error(
            "The configured webhook URL must start with https://. "
            "Check the N8N_WEBHOOK_URL value in Streamlit Secrets."
        )

    else:
        payload = dict(case)
        payload["submitted_at_utc"] = datetime.utcnow().isoformat() + "Z"
        payload["source"] = "Sentinel Streamlit Dashboard"
        payload["human_review_required"] = True

        try:
            with st.spinner(
                "Submitting case to n8n and waiting for the workflow response..."
            ):
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=90,
                )

            response.raise_for_status()

            st.session_state.last_case_id = case["case_id"]
            st.session_state.last_run_time = datetime.now().strftime(
                "%d %b %Y, %I:%M:%S %p"
            )

            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text

            st.session_state.last_response = {
                "http_status": response.status_code,
                "data": response_data,
            }

            st.success(
                f"n8n returned an HTTP {response.status_code} response "
                f"for {case['case_id']}."
            )

        except requests.Timeout:
            st.error(
                "The request timed out while waiting for n8n. "
                "Check the workflow execution in n8n before retrying."
            )

        except requests.RequestException as error:
            st.error(
                "The request could not be completed. Check the Production "
                "Webhook URL, n8n execution status and webhook response "
                "configuration."
            )
            st.code(str(error))


# ============================================================
# 14. DISPLAY WORKFLOW RESPONSE
# ============================================================

if st.session_state.last_response is not None:
    st.divider()

    st.markdown(
        '<div class="section-heading">Latest workflow response</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="case-note">
            <strong>Case submitted:</strong> {st.session_state.last_case_id}<br>
            <strong>Response received:</strong> {st.session_state.last_run_time}<br>
            <strong>HTTP status:</strong> {st.session_state.last_response["http_status"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    response_data = st.session_state.last_response["data"]

    if isinstance(response_data, (dict, list)):
        st.json(response_data)
    elif response_data:
        st.code(str(response_data), language="text")
    else:
        st.info(
            "n8n returned an empty response. Check the workflow's webhook "
            "response settings and final output configuration."
        )

    st.markdown(
        """
        <div class="governance-box">
            <strong>Human decision pending.</strong> Review the returned
            evidence, risk indicators, missing information and routing outcome.
            A human investigator remains responsible for the final decision.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 15. TRANSPARENCY AND GOVERNANCE
# ============================================================

with st.expander("View full synthetic case payload"):
    st.json(case)

with st.expander("Governance controls and limitations"):
    st.markdown(
        """
        **Data and privacy**
        - This prototype uses synthetic customer and transaction data only.
        - Do not enter real customer information or confidential bank records.

        **Evidence and uncertainty**
        - Partial or conflicting evidence must be visible to the investigator.
        - A missing verification record must not be treated as proof of fraud.
        - Risk scores and routing labels are illustrative, not validated
          production fraud decisions.

        **Human oversight**
        - The workflow is decision support, not an autonomous enforcement system.
        - A human investigator retains final decision authority.
        - No automatic account freeze or transaction blocking is permitted.

        **Auditability**
        - Record test cases, workflow executions, outputs and reviewer feedback
          for project evaluation.
        - Validate the workflow's behaviour before drawing conclusions.
        """
    )

st.markdown(
    """
    <div class="footer">
        SENTINEL · Governed Agentic AI for Banking Fraud Investigation and Response<br>
        Student proof of concept · Synthetic data only · Human oversight required<br>
        Not intended for production banking or autonomous fraud enforcement
    </div>
    """,
    unsafe_allow_html=True,
)
