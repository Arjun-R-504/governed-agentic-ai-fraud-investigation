
import streamlit as st
import requests
import json
from datetime import datetime

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sentinel | Fraud Investigation",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. SECURE N8N CONFIGURATION
# ============================================================
# Configure this in Streamlit Cloud > App settings > Secrets.
# Do NOT paste the production webhook URL into this public file.
#
# Required Streamlit Secret:
# N8N_WEBHOOK_URL = "your-n8n-production-webhook-url"

try:
    N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
except (KeyError, FileNotFoundError):
    N8N_WEBHOOK_URL = ""

# ============================================================
# 3. DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #101b32;
        --blue: #3563e9;
        --cyan: #35c6d5;
        --ink: #18243a;
        --muted: #68758a;
        --line: #e5eaf2;
        --surface: #ffffff;
        --background: #f4f7fb;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
    }

    [data-testid="stHeader"] {
        background: rgba(244,247,251,0.92);
    }

    [data-testid="stSidebar"] {
        background: #101b32;
    }

    [data-testid="stSidebar"] * {
        color: #e9efff;
    }

    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: white;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
        letter-spacing: -0.5px;
    }

    .hero {
        background: linear-gradient(120deg, #101b32 0%, #203e77 72%, #286c94 100%);
        padding: 30px 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 30px rgba(16,27,50,0.12);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: -55px;
        top: -90px;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 50%;
        box-shadow: 0 0 0 30px rgba(255,255,255,0.035),
                    0 0 0 60px rgba(255,255,255,0.025);
    }

    .hero-kicker {
        color: #8fe9ef;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .hero-title {
        color: white;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(25px, 3vw, 36px);
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .hero-copy {
        color: #d8e4fa;
        max-width: 760px;
        line-height: 1.65;
        font-size: 14px;
    }

    .hero-tag {
        display: inline-block;
        border: 1px solid rgba(143,233,239,0.45);
        color: #b5f3f4;
        background: rgba(53,198,213,0.10);
        padding: 6px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 14px;
    }

    .section-label {
        color: #52627a;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 24px 0 10px 0;
    }

    .metric-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 17px 18px;
        min-height: 112px;
        box-shadow: 0 3px 12px rgba(22,39,70,0.025);
    }

    .metric-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .metric-value {
        color: var(--ink);
        font-family: 'Manrope', sans-serif;
        font-size: 27px;
        font-weight: 800;
        line-height: 1.25;
    }

    .metric-note {
        color: #7c899c;
        font-size: 11px;
        margin-top: 6px;
    }

    .panel {
        background: white;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 21px;
        margin-bottom: 15px;
        box-shadow: 0 3px 12px rgba(22,39,70,0.025);
    }

    .panel-title {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .panel-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 15px;
    }

    .status-pill {
        display: inline-block;
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
        background: #edf2ff;
        color: #3159bf;
    }

    .governance-box {
        background: #eef8f6;
        border: 1px solid #d0ece5;
        border-radius: 13px;
        padding: 15px 17px;
        color: #23594e;
        font-size: 13px;
        line-height: 1.65;
    }

    .notice-box {
        background: #fff8e9;
        border: 1px solid #f3e2b7;
        border-radius: 12px;
        padding: 13px 15px;
        color: #77551c;
        font-size: 12px;
        line-height: 1.6;
    }

    .case-id {
        color: #3563e9;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #3563e9, #287fbb);
        border: 0;
        border-radius: 10px;
        padding: 0.68rem 1.2rem;
        font-weight: 700;
        min-height: 46px;
        box-shadow: 0 5px 13px rgba(53,99,233,0.18);
    }

    div.stButton > button[kind="primary"]:hover {
        background: #244fc8;
        border: 0;
    }

    div[data-testid="stSelectbox"] label {
        font-weight: 600;
        color: #34435a;
    }

    hr {
        border-color: var(--line);
    }

    .footer {
        text-align: center;
        color: #8490a2;
        font-size: 11px;
        padding-top: 20px;
        line-height: 1.8;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 4. SYNTHETIC FRAUD CASES
# ============================================================

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
        "scenario": "Normal",
        "case_notes": (
            "The transaction is larger than the customer's usual amount, "
            "but the device, location and verification are familiar."
        )
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
            "The new device and unfamiliar location raise questions, "
            "but the available verification record is not conclusive."
        )
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
            "Multiple unusual indicators and incomplete evidence "
            "warrant urgent review by a human investigator."
        )
    }
}

# ============================================================
# 5. SESSION STATE
# ============================================================

if "investigation_result" not in st.session_state:
    st.session_state.investigation_result = None

if "investigated_case_id" not in st.session_state:
    st.session_state.investigated_case_id = None

if "investigation_timestamp" not in st.session_state:
    st.session_state.investigation_timestamp = None

# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:10px 0 20px 0;">
            <div style="font-size:27px;">🔎</div>
            <div style="font-family:Manrope;font-size:21px;font-weight:800;">
                SENTINEL
            </div>
            <div style="font-size:11px;color:#a9b9d8;letter-spacing:1.5px;">
                FRAUD INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("**INVESTIGATION WORKSPACE**")
    st.caption("Select a synthetic case in the main dashboard to begin.")

    st.markdown("---")
    st.markdown("**WORKFLOW STATUS**")

    if N8N_WEBHOOK_URL:
        st.success("Secure URL configured")
    else:
        st.warning("Webhook secret not configured")

    st.markdown("---")
    st.markdown("**GOVERNANCE CONTROLS**")
    st.markdown(
        """
        - Human investigator has final authority
        - Evidence gaps remain visible
        - Uncertainty is not treated as proof
        - No automatic account freezing
        - No automatic transaction blocking
        """
    )

    st.markdown("---")
    st.caption("Academic prototype • Synthetic data only")

# ============================================================
# 7. HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Governed Agentic AI • Banking Operations</div>
        <div class="hero-title">
            Banking Fraud<br>Investigation & Response
        </div>
        <div class="hero-copy">
            A human-supervised investigation workspace that brings together
            transaction triage, evidence validation, illustrative risk
            assessment and investigation routing through an n8n workflow.
        </div>
        <div class="hero-tag">
            ● SYNTHETIC DATA &nbsp; | &nbsp; HUMAN-IN-THE-LOOP
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 8. TOP SUMMARY METRICS
# ============================================================

st.markdown('<div class="section-label">Investigation overview</div>',
            unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Synthetic test cases</div>
            <div class="metric-value">03</div>
            <div class="metric-note">Available for demonstration</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Workflow stages</div>
            <div class="metric-value">05</div>
            <div class="metric-note">Triage to case routing</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Decision authority</div>
            <div class="metric-value" style="font-size:22px;">Human</div>
            <div class="metric-note">Final decision stays with investigator</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Automated enforcement</div>
            <div class="metric-value" style="font-size:22px;">Disabled</div>
            <div class="metric-note">No automatic freezing or blocking</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# 9. CASE SELECTION AND DETAILS
# ============================================================

st.markdown('<div class="section-label">01 / Case selection</div>',
            unsafe_allow_html=True)

left, right = st.columns([1.05, 1.45], gap="large")

with left:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Select investigation case</div>
            <div class="panel-subtitle">
                Choose one of the three predefined synthetic scenarios.
            </div>
        """,
        unsafe_allow_html=True
    )

    selected_case_label = st.selectbox(
        "Synthetic case",
        list(cases.keys()),
        key="selected_case_label"
    )

    case = cases[selected_case_label]

    st.markdown(
        f"""
        <div class="case-id">{case['case_id']}</div>
        <h3 style="margin:5px 0 8px 0;">{case['scenario']} scenario</h3>
        <p style="font-size:13px;color:#68758a;line-height:1.6;">
            {case['case_notes']}
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Transaction snapshot</div>
            <div class="panel-subtitle">
                Review the supplied transaction and account indicators.
            </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Transaction amount",
            f"₹{case['transaction_amount']:,}"
        )
        st.write("**Case ID:**", case["case_id"])
        st.write("**Customer ID:**", case["customer_id"])
        st.write("**Channel:**", case["channel"])

    with c2:
        st.metric(
            "Usual transaction amount",
            f"₹{case['usual_amount']:,}"
        )
        st.write("**Device:**", case["device"])
        st.write("**Location:**", case["location"])
        st.write("**Evidence:**", case["evidence_status"])

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 10. INDICATORS AND EVIDENCE
# ============================================================

st.markdown('<div class="section-label">02 / Indicators & evidence</div>',
            unsafe_allow_html=True)

a, b, c, d = st.columns(4)

with a:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Failed login attempts</div>
            <div class="metric-value">{case['failed_logins']}</div>
            <div class="metric-note">Supplied synthetic indicator</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Previous alerts</div>
            <div class="metric-value">{case['previous_alerts']}</div>
            <div class="metric-note">Supplied synthetic indicator</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Device familiarity</div>
            <div class="metric-value" style="font-size:20px;">
                {"Known" if case['device'] == "Known device" else "New"}
            </div>
            <div class="metric-note">{case['device']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with d:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Verification</div>
            <div class="metric-value" style="font-size:18px;">
                {
                    "Confirmed"
                    if case["verification_status"] == "Confirmed legitimate"
                    else "Needs review"
                }
            </div>
            <div class="metric-note">Review source evidence</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with st.expander("View complete synthetic case record"):
    st.json(case)

# ============================================================
# 11. INVESTIGATION WORKFLOW
# ============================================================

st.markdown('<div class="section-label">03 / Run investigation</div>',
            unsafe_allow_html=True)

st.markdown(
    """
    <div class="panel">
        <div class="panel-title">Governed investigation workflow</div>
        <div class="panel-subtitle">
            The selected case is sent to the n8n Production Webhook.
            The workflow response is displayed below for human review.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px 0;">
        <span class="status-pill">01 · Transaction triage</span>
        <span class="status-pill">02 · Evidence validation</span>
        <span class="status-pill">03 · Risk assessment</span>
        <span class="status-pill">04 · Case report</span>
        <span class="status-pill">05 · Human routing</span>
    </div>
    """,
    unsafe_allow_html=True
)

run_col, info_col = st.columns([1, 2])

with run_col:
    run_investigation = st.button(
        "🔎  Run Investigation",
        type="primary",
        use_container_width=True
    )

with info_col:
    st.caption(
        "This action submits only the selected synthetic case. "
        "It does not contact a real bank or execute a financial action."
    )

if run_investigation:
    if not N8N_WEBHOOK_URL:
        st.error(
            "The n8n URL is not configured in Streamlit Secrets. "
            "Add the N8N_WEBHOOK_URL secret in your Streamlit app settings, "
            "save it, and allow the app to reload."
        )
    else:
        try:
            with st.spinner(
                "Submitting the case to n8n and waiting for the workflow response..."
            ):
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json=case,
                    headers={"Content-Type": "application/json"},
                    timeout=90
                )

            response.raise_for_status()

            try:
                result = response.json()
            except ValueError:
                result = {"workflow_response": response.text}

            st.session_state.investigation_result = result
            st.session_state.investigated_case_id = case["case_id"]
            st.session_state.investigation_timestamp = datetime.now().strftime(
                "%d %b %Y, %I:%M:%S %p"
            )

        except requests.Timeout:
            st.error(
                "The request timed out while waiting for n8n. "
                "Check whether the workflow completed and whether the "
                "Webhook node is configured to return a response."
            )

        except requests.RequestException as error:
            st.error(
                "Could not complete the n8n request. "
                "Check that the Production Webhook is active and that "
                "the URL in Streamlit Secrets is correct."
            )
            with st.expander("Technical error details"):
                st.code(str(error))

# ============================================================
# 12. INVESTIGATION RESULTS
# ============================================================

result = st.session_state.investigation_result

if result is not None:
    st.markdown(
        '<div class="section-label">04 / Investigation output</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"Workflow response received for "
        f"{st.session_state.investigated_case_id}."
    )

    st.caption(
        f"Received at: {st.session_state.investigation_timestamp}"
    )

    # n8n may return one object or a list of output objects.
    # Display the original response without losing any fields.
    result_data = result

    if isinstance(result_data, list) and len(result_data) == 1:
        result_data = result_data[0]

    # Handle a common n8n response shape: {"data": {...}}
    if isinstance(result_data, dict):
        if isinstance(result_data.get("data"), dict):
            display_result = result_data["data"]
        else:
            display_result = result_data
    else:
        display_result = result_data

    if isinstance(display_result, dict):
        routing = display_result.get("routing_status")
        risk_level = display_result.get("risk_level")
        risk_score = display_result.get("risk_score")
        final_decision = display_result.get("final_decision")
        evidence_status = display_result.get("evidence_review_status")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Illustrative risk level</div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-value" style="font-size:23px;">'
                f'{risk_level if risk_level is not None else "See report"}'
                f'</div></div>',
                unsafe_allow_html=True
            )

        with r2:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Illustrative risk score</div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-value" style="font-size:23px;">'
                f'{risk_score if risk_score is not None else "N/A"}'
                f'</div></div>',
                unsafe_allow_html=True
            )

        with r3:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Evidence review</div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metric-value" style="font-size:18px;">'
                f'{evidence_status if evidence_status is not None else "See report"}'
                f'</div></div>',
                unsafe_allow_html=True
            )

        if routing:
            st.markdown("#### Recommended investigation route")
            st.info(str(routing))

        if final_decision:
            st.markdown("#### Final decision status")
            st.warning(str(final_decision))

    st.markdown(
        """
        <div class="governance-box">
            <strong>Human oversight required</strong><br>
            This output supports investigation only. It is not proof of fraud.
            An authorised human investigator must examine the evidence and
            make the final decision. The prototype cannot freeze accounts,
            block transactions or take other consequential financial actions.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("View complete n8n response"):
        st.json(result)

else:
    st.info(
        "No investigation result is available yet. Select a synthetic case "
        "and click **Run Investigation** to send it to n8n."
    )

# ============================================================
# 13. GOVERNANCE AND LIMITATIONS
# ============================================================

st.markdown(
    '<div class="section-label">05 / Governance & responsible use</div>',
    unsafe_allow_html=True
)

g1, g2 = st.columns(2, gap="large")

with g1:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Governance safeguards</div>
            <div class="panel-subtitle">
                Controls built into the intended investigation process.
            </div>
            <div class="governance-box">
                ✓ Human investigator retains final authority<br>
                ✓ Missing evidence should remain visible<br>
                ✓ Conflicting records require further review<br>
                ✓ Risk scores are decision-support indicators only<br>
                ✓ No autonomous account freezing or transaction blocking
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with g2:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Prototype limitations</div>
            <div class="panel-subtitle">
                Important boundaries for interpreting results.
            </div>
            <div class="notice-box">
                This academic prototype uses synthetic cases and illustrative
                rules. Its outputs are not a validated fraud-detection model
                and must not be used for real banking decisions. Model
                validation, security testing, auditability and authorised
                expert review would be required before any real-world use.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# 14. FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        SENTINEL · GOVERNED AGENTIC AI FOR BANKING FRAUD INVESTIGATION<br>
        Academic demonstration • Synthetic data only • Human-supervised response<br>
        Designed to support investigation, not to replace human judgement.
    </div>
    """,
    unsafe_allow_html=True
)
