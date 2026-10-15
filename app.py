
import streamlit as st
import pickle
import pandas as pd
from pathlib import Path


from database import (
    initialize_database,
    load_applications,
    load_funding_records,
    save_application,
    update_application_status,
    save_funding_record,
    save_repayment,
    load_repayments
)



st.set_page_config(
    page_title="PeerFin AI",
    page_icon="💰",
    layout="wide"
)
initialize_database()

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
        color: #1f2937;
    }

    [data-testid="stSidebar"] {
        background-color: #10243a;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: white !important;
    }

    h1 {
        color: #163a5f;
    }

    h2, h3 {
        color: #24527a;
    }

   
[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #dbe5ef;
    box-shadow: 0 3px 10px rgba(16, 36, 58, 0.08);
}

[data-testid="stMetricLabel"] {
    color: #526579;
    font-size: 14px;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #163a5f;
    font-size: 28px;
    font-weight: 750;
}

[data-testid="stMetricDelta"] {
    font-size: 13px;
}

    div.stButton > button {
        background-color: #176b87;
        color: white;
        border-radius: 8px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #124e66;
        color: white;
    }

/* Make radio labels readable */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    color: #163a5f !important;
}

/* Keep radio controls visible */
div[data-testid="stRadio"] input {
    accent-color: #176b87;
}

/* Improve Home page readability */
.stApp {
    background-color: #f4f7fb;
}

/* Make form labels dark and readable */
.stApp label,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stWidgetLabel"] {
    color: #183153 !important;
    opacity: 1 !important;
}

/* Improve text input and number input appearance */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    color: #183153 !important;
}

/* Keep input fields clean and readable */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    background-color: #ffffff !important;
}

/* Improve main page text visibility */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #183153;
}
</style>
""", unsafe_allow_html=True)


# Load AI model
MODEL_PATH = Path(__file__).parent / "models" / "risk_model.pkl"

with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

# Load saved applications from SQLite
if "applications" not in st.session_state:
    st.session_state.applications = load_applications()



if "funding_records" not in st.session_state:
    st.session_state.funding_records = load_funding_records()



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None


# Login screen
if not st.session_state.logged_in:
    st.title("💰 PeerFin AI")
    st.subheader("Peer-to-Peer Lending Platform")
    st.write("Welcome! Choose your role to continue.")

    role = st.radio(
        "I want to continue as:",
        ["Borrower", "Lender"],
        horizontal=True
    )

    if st.button("Continue"):
        st.session_state.user_role = role
        st.session_state.logged_in = True
        st.rerun()

    st.info("Educational demo only. No real money is transferred.")
    st.stop()


st.title("💰 PeerFin AI")
st.subheader("AI-Based P2P Lending Platform")

# Sidebar navigation
st.sidebar.success(
    f"Logged in as: {st.session_state.user_role}"
)

if st.sidebar.button("🔄 Switch Role"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()


if st.session_state.user_role == "Borrower":
    pages = ["Home", "Dashboard", "Loan Tracking", "Repayment Tracking"]
else:
    pages = ["Lender Dashboard", "Loan Requests", "Funding History"]

page = st.sidebar.radio("Navigate to", pages)


applications = st.session_state.applications

# HOME PAGE
if page == "Home":
    st.header("📝 Loan Application")
    st.write("Apply for an educational demo loan.")

    with st.form("loan_form"):
        borrower = st.text_input("Your Name")

        amount = st.number_input(
            "Loan Amount (₹)", min_value=1000,
            max_value=100000, value=10000, step=1000
        )

        purpose = st.selectbox(
            "Loan Purpose",
            ["Education", "Business", "Medical", "Personal"]
        )

        duration = st.selectbox(
            "Loan Duration", [3, 6, 9, 12],
            format_func=lambda x: f"{x} months"
        )

        monthly_income = st.number_input(
            "Monthly Income (₹)", min_value=0,
            value=15000, step=1000
        )

        debt = st.number_input(
            "Existing Debt (₹)", min_value=0,
            value=0, step=1000
        )

        late_payments = st.number_input(
            "Previous Late Payments", min_value=0,
            max_value=5, value=0, step=1
        )

        submitted = st.form_submit_button("Submit Loan Application")

    if submitted:
        if not borrower.strip():
            st.error("Please enter your name.")
        else:
            features = [[monthly_income, amount, debt, late_payments]]
            prediction = int(model.predict(features)[0])
            
            new_application = {
                "borrower": borrower.strip(),
                "amount": amount,
                "purpose": purpose,
                "duration": duration,
                "risk": prediction,
                "status": "Pending"
            }

            new_application["id"] = save_application(new_application)
            applications.append(new_application)



            
            st.success("Demo loan application submitted!")

            if prediction == 1:
                st.warning("AI Demo Result: Higher Risk")
            else:
                st.success("AI Demo Result: Lower Risk")

            st.write("### Application Details")
            st.write("Borrower:", borrower)
            st.write(f"Loan Amount: ₹{amount:,.0f}")
            st.write("Purpose:", purpose)
            st.write("Duration:", f"{duration} months")
            st.write(f"Monthly Income: ₹{monthly_income:,.0f}")

            st.caption(
                "This model uses synthetic training data. "
                "Its risk prediction is for educational demonstration only."
            )
            st.info("No real loan or money transfer occurs.")


# DASHBOARD PAGE
elif page == "Dashboard":
    st.header("📊 PeerFin AI Dashboard")

    total = len(applications)
    total_amount = sum(app["amount"] for app in applications)
    approved = sum(app["status"] == "Approved" for app in applications)
    pending = sum(app["status"] == "Pending" for app in applications)
    rejected = sum(app["status"] == "Rejected" for app in applications)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", total)
    col2.metric("Total Loan Amount", f"₹{total_amount:,.0f}")
    col3.metric("Approved Loans", approved)

    col4, col5 = st.columns(2)
    col4.metric("Pending Applications", pending)
    col5.metric("Rejected Applications", rejected)

    st.subheader("🕒 Recent Applications")

    if applications:
        for app in applications[-5:][::-1]:
            st.write(
                f"**{app['borrower']}** — "
                f"₹{app['amount']:,.0f} — "
                f"{app['status']}"
            )
    else:
        st.info("No applications available yet.")


# LOAN TRACKING PAGE
elif page == "Loan Tracking":
    st.header("📋 Loan Tracking")

    if applications:
        tracking_data = []

        for app in applications:
            tracking_data.append({
                "Borrower": app["borrower"],
                "Loan Amount": f"₹{app['amount']:,.0f}",
                "Purpose": app.get("purpose", "N/A"),
                "Status": app["status"]
            })

        st.dataframe(tracking_data, use_container_width=True)
        st.subheader("My Loan Status")

        for app in applications:
            st.write(f"### {app['borrower']}")
            st.write(f"Loan Amount: ₹{app['amount']:,.0f}")

            status = app.get("status", "Pending")

            if status == "Approved":
                st.success("✅ Your loan application has been APPROVED!")
            elif status == "Rejected":
                st.error("❌ Your loan application has been REJECTED.")
            else:
                st.info("⏳ Your loan application is PENDING review.")

            st.divider()

       
    else:
        st.info("No demo loan applications submitted yet.")


# REPAYMENT TRACKING PAGE
elif page == "Repayment Tracking":
    st.header("💳 Repayment Tracking")

    approved_applications = [
        app for app in applications
        if app["status"] == "Approved"
    ]

    if approved_applications:
        selected_app = st.selectbox(
            "Select an approved loan",
            approved_applications,
            format_func=lambda app: (
                f"{app['borrower']} — "
                f"₹{app['amount']:,.0f}"
            ),
            key="repayment_loan_select"
        )

        repayments = load_repayments()

        loan_repayments = [
            r for r in repayments
            if r["Application ID"] == selected_app["id"]
        ]

        total_repaid = sum(
            r["Amount"] for r in loan_repayments
        )

        principal = float(selected_app["amount"])
        interest_rate = float(selected_app.get("interest_rate", 10.0))
        duration = int(selected_app.get("duration", 12))

        estimated_interest = (
            principal * interest_rate * duration
        ) / (100 * 12)

        total_due = principal + estimated_interest
        remaining = max(0, total_due - total_repaid)

        st.metric(
            "Original Loan Amount",
            f"₹{selected_app['amount']:,.0f}"
        )
        st.metric("Total Repaid", f"₹{total_repaid:,.0f}")
        st.metric("Remaining Balance", f"₹{remaining:,.0f}")

        st.info(
            "Demo only. No real payments are processed."
        )

        if remaining > 0:
            repayment_amount = st.number_input(
                "Demo Repayment Amount (₹)",
                min_value=1,
                max_value=int(remaining),
                value=min(500, int(remaining)),
                step=500,
                key="repayment_amount_input"
            )

            if st.button("Record Simulated Repayment"):
                repayment_record = {
                    "Application ID": selected_app["id"],
                    "Borrower": selected_app["borrower"],
                    "Amount": float(repayment_amount),
                    "Note": "Demo only — no money transferred"
                }

                save_repayment(repayment_record)

                st.success("Simulated repayment saved!")
                st.rerun()
        else:
            st.success("This demo loan has been fully repaid.")

        st.subheader("Repayment History")

        if loan_repayments:
            st.dataframe(
                [
                    {
                        "Date/Record ID": r["ID"],
                        "Amount": r["Amount"],
                        "Note": r["Note"]
                    }
                    for r in loan_repayments
                ],
                use_container_width=True
            )
        else:
            st.info("No repayments recorded for this loan yet.")

    else:
        st.info("No approved loans available for repayment tracking.")

# LENDER DASHBOARD
if page == "Lender Dashboard":
    st.header("💰 Lender Dashboard")
    st.write("Welcome to the PeerFin AI Lender Portal.")

    total_requests = len(applications)

    total_requested = sum(
        app["amount"] for app in applications
    )

    approved_loans = sum(
        app["status"] == "Approved"
        for app in applications
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Loan Requests", total_requests)

    col2.metric(
        "Total Requested Amount",
        f"₹{total_requested:,.0f}"
    )

    col3.metric("Approved Loans", approved_loans)
    st.subheader("🤖 AI Credit Risk Analysis")

    high_risk = sum(
        app["risk"] == 1 for app in applications
    )

    low_risk = sum(
        app["risk"] == 0 for app in applications
    )

    col4, col5 = st.columns(2)

    col4.metric("🔴 Higher Risk Applications", high_risk)
    col5.metric("🟢 Lower Risk Applications", low_risk)

    if applications:
        total = len(applications)

        high_percent = (high_risk / total) * 100
        low_percent = (low_risk / total) * 100

        st.write(f"🔴 Higher Risk: {high_percent:.1f}%")
        st.write(f"🟢 Lower Risk: {low_percent:.1f}%")

    if applications:
        risk_data = pd.DataFrame({
            "Risk Level": ["Higher Risk", "Lower Risk"],
            "Applications": [high_risk, low_risk]
        })

        st.bar_chart(
            risk_data,
            x="Risk Level",
            y="Applications"
        )
    else:
        st.info("No applications available for risk analysis yet.")


    st.info(
        "This is an educational simulation. "
        "No real money is invested or transferred."
    )

# LOAN REQUESTS PAGE
if page == "Loan Requests":
    st.header("📋 Loan Requests")
    st.write("View loan applications submitted by borrowers.")

    if applications:
        lender_requests = []

        for app in applications:
            lender_requests.append({
                "Borrower": app["borrower"],
                "Loan Amount": f"₹{app['amount']:,.0f}",
                "Purpose": app.get("purpose", "N/A"),
                "AI Risk": (
                    "Higher Risk"
                    if app["risk"] == 1
                    else "Lower Risk"
                ),
                "Status": app.get("status", "Pending")
            })

        st.dataframe(
            lender_requests,
            use_container_width=True
        )
        st.subheader("Review Loan Application")

        selected_index = st.selectbox(
            "Select a loan request",
            range(len(applications)),
            format_func=lambda i: (
                f"{applications[i]['borrower']} — "
                f"₹{applications[i]['amount']:,.0f} "
                f"({applications[i].get('status', 'Pending')})"
            ),
            key="lender_review_select"
        )

        selected_app = applications[selected_index]

        st.write("**Borrower:**", selected_app["borrower"])
        st.write("**Loan Amount:**", f"₹{selected_app['amount']:,.0f}")
        st.write("**Purpose:**", selected_app.get("purpose", "N/A"))
        st.write(
            "**AI Risk:**",
            "Higher Risk" if selected_app["risk"] == 1
            else "Lower Risk"
        )
        st.write("**Current Status:**", selected_app.get("status", "Pending"))
        st.subheader("📈 Loan Interest Settings")

        interest_rate = st.number_input(        
    "Annual Interest Rate (%)",
    min_value=0.0,
    max_value=36.0,
    value=float(selected_app.get("interest_rate", 10.0)),
    step=0.5,
    key=f"interest_rate_{selected_app['id']}"
)

        loan_duration = int(selected_app.get("duration", 12))

        principal = float(selected_app["amount"])
        estimated_interest = (
            principal * interest_rate * loan_duration
        ) / (100 * 12)

        total_repayment = principal + estimated_interest

        col_a, col_b, col_c = st.columns(3)

        col_a.metric("Loan Principal", f"₹{principal:,.2f}")
        col_b.metric("Estimated Interest", f"₹{estimated_interest:,.2f}")
        col_c.metric("Total Repayment", f"₹{total_repayment:,.2f}")

        st.caption(
            "Illustrative simple-interest estimate. "
            "The rate is annual and the duration is in months."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve Loan", key="lender_approve"):
                selected_app["status"] = "Approved"
                selected_app["interest_rate"] = interest_rate

                update_application_status(
                    selected_app["id"], "Approved"
                )

                from database import save_interest_rate
                save_interest_rate(
                    selected_app["id"], interest_rate
                )

                st.success("Loan approved with the selected interest rate!")
                st.rerun()

        with col2:
            if st.button("❌ Reject Loan", key="lender_reject"):
                selected_app["status"] = "Rejected"
                update_application_status(
                    selected_app["id"], "Rejected"
                )
                st.warning("Loan rejected in the demo!")
                st.rerun()


        st.subheader("💸 Simulate Funding")

        eligible_apps = [
            i for i, app in enumerate(applications)
            if app.get("status") == "Approved"
        ]

        if eligible_apps:
            selected_index = st.selectbox(
                "Select an approved loan",
                eligible_apps,
                format_func=lambda i: (
                    f"{applications[i]['borrower']} — "
                    f"₹{applications[i]['amount']:,.0f}"
                ),
                key="funding_loan_select"
            )

            funding_amount = st.number_input(
                "Simulated funding amount (₹)",
                min_value=1,
                max_value=int(
                    applications[selected_index]["amount"]
                ),
                value=int(
                    applications[selected_index]["amount"]
                ),
                step=500,
                key="funding_amount_input"
            )

           
            if st.button("Record Simulated Funding"):
                selected_funding_app = applications[selected_index]

                funding_record = {
                    "Application ID": selected_funding_app["id"],
                    "Borrower": selected_funding_app["borrower"],
                    "Loan Amount": int(selected_funding_app["amount"]),
                    "Amount": int(funding_amount),
                    "Purpose": selected_funding_app["purpose"],
                    "Note": "Demo only — no money transferred"
                }

                save_funding_record(funding_record)
                st.session_state.funding_records = load_funding_records()

                st.success("Simulated funding recorded!")
                st.rerun()

        else:
            st.info(
                "No approved loans available. "
                "Approve a demo loan before recording funding."
            )


    else:
        st.info(
            "No loan requests available. "
            "Submit a demo application as a borrower first."
        )

    st.info(
        "Educational demo only. No real money is transferred."
    )

# FUNDING HISTORY PAGE
if page == "Funding History":
    st.header("📜 Funding History")
    st.write("View your simulated loan funding records.")

    funding_records = load_funding_records()
    st.session_state.funding_records = funding_records

    if funding_records:
        st.dataframe(
            funding_records,
            use_container_width=True
        )

        total_funded = sum(
            record["Amount"]
            for record in funding_records
        )

        st.metric(
            "Total Simulated Funding",
            f"₹{total_funded:,.0f}"
        )
    else:
        st.info(
            "No funding records yet. "
            "Funding records will appear here when demo funding is recorded."
        )

    st.warning(
        "Educational simulation only. No real money is transferred."
    )
