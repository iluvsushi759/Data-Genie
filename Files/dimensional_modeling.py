import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

# Initialize session state keys if they don't exist
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

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

    # ⭐ NEW: Evaluation Mode Toggle
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

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 📊 FEEDBACK BUTTON (Only if Evaluation Mode is ON)
# ============================================================

if (
    st.session_state.chat_complete
    and not st.session_state.feedback_shown
    and st.session_state.evaluation_mode
):
    if st.button("Get Dimensional Model Evaluation"):
        st.session_state.feedback_shown = True

# ============================================================
# 📝 FEEDBACK SECTION (Only if Evaluation Mode is ON)
# ============================================================

if st.session_state.feedback_shown and st.session_state.evaluation_mode:

    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("📊 Dimensional Model Evaluation")

    conversation_history = "\n".join(
        [f"{m['role']}: {m['content']}"
         for m in st.session_state.messages]
    )

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback = feedback_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a Principal Data Architect evaluating a dimensional model.

Score 1–10 based on:
- Grain correctness
- Additivity correctness
- Conformed dimension design
- SCD strategy
- Business alignment
- Simplicity vs completeness

Format exactly:

Overall Score: X/10

Strengths:
- ...
- ...

Weaknesses:
- ...
- ...

Improvements:
- ...
- ...

Do not ask additional questions.
"""
            },
            {
                "role": "user",
                "content": f"Evaluate this dimensional modeling discussion:\n{conversation_history}"
            }
        ]
    )

    st.write(feedback.choices[0].message.content)

    if st.button("Restart Simulation", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

    st.markdown('</div>', unsafe_allow_html=True)
