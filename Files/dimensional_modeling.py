import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

# ===============================
# Initialize session state keys
# ===============================
session_keys_defaults = {
    "setup_complete": False,
    "feedback_shown": False,
    "evaluation_mode": False,
    "ai_response": ""
}

for key, default_value in session_keys_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ============================================================
# 🔐 PASSWORD PROTECTION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Secure Access", page_icon="🔐")
    password = st.text_input("Enter Password", type="password")
    if "APP_PASSWORD" in st.secrets and password == st.secrets["APP_PASSWORD"]:
        st.session_state.authenticated = True
        st.experimental_rerun()
    else:
        st.stop()

# ============================================================
# ⚙ SETUP PHASE
# ============================================================

if not st.session_state.setup_complete:

    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("⚙ Business Process Configuration")

    business_process = st.text_area(
        "Describe the business process you want to model",
        placeholder="Example: Students use meal cards at campus food locations..."
    )

    grain = st.text_input(
        "Define the grain (the atomic level of the fact table)",
        placeholder="Example: One row per student per food location per day"
    )

    source_tables = st.text_area(
        "List your source tables",
        placeholder="Example: Student, Campus_Food, Meal_Card_Transactions..."
    )

    kpis = st.text_area(
        "List the KPIs or measures you care about",
        placeholder="Example: Daily balance, total spend, number of swipes..."
    )

    evaluation_mode = st.checkbox(
        "Enable Evaluation Mode (Optional)",
        value=False
    )

    if st.button("Start Modeling"):
        st.session_state.business_process = business_process
        st.session_state.grain = grain
        st.session_state.source_tables = source_tables
        st.session_state.kpis = kpis
        st.session_state.evaluation_mode = evaluation_mode
        st.session_state.setup_complete = True

        # Call AI immediately for basic analysis
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        prompt = f"""
You are a Principal Data Architect. 
Given the following inputs:

Business Process: {business_process}
Grain: {grain}
Source Tables: {source_tables}
KPIs: {kpis}

Provide a clear summary of a dimensional model design: facts, dimensions, and any obvious observations or recommendations.
Respond concisely.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        st.session_state.ai_response = response.choices[0].message.content

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 📊 DISPLAY AI RESPONSE
# ============================================================

if st.session_state.setup_complete:
    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("📊 Dimensional Model Summary")
    st.write(st.session_state.ai_response or "✅ Setup Complete. Your AI response will appear here after clicking Start Modeling.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 📊 EVALUATION MODE (Optional)
# ============================================================

if st.session_state.setup_complete and st.session_state.evaluation_mode and not st.session_state.feedback_shown:

    if st.button("Get Evaluation"):
        feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        feedback_prompt = f"""
You are a Principal Data Architect evaluating a dimensional model.

Inputs:
Business Process: {st.session_state.business_process}
Grain: {st.session_state.grain}
Source Tables: {st.session_state.source_tables}
KPIs: {st.session_state.kpis}

Analyze the model and provide:
- Score 1–10
- Strengths
- Weaknesses
- Improvements
"""
        feedback_response = feedback_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": feedback_prompt}]
        )
        st.session_state.feedback_shown = True
        st.session_state.feedback = feedback_response.choices[0].message.content

# Display feedback if available
if st.session_state.feedback_shown:
    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("📊 Dimensional Model Evaluation")
    st.write(st.session_state.feedback)
    if st.button("Restart Simulation", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
    st.markdown('</div>', unsafe_allow_html=True)
