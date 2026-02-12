import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

# ============================================================
# 🔐 PASSWORD PROTECTION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Secure Access", page_icon="🔐")
    password = st.text_input("Enter Password", type="password")
    if password == st.secrets["APP_PASSWORD"]:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

# ============================================================
# 🖥 PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Architecture Strategy Simulator", page_icon="🏗")

# ============================================================
# 🎨 CUSTOM PROFESSIONAL DARK UI (BRIGHT TEXT + FIXED DROPDOWNS)
# ============================================================

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #1b1f28; /* app background */
}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

/* Unified bright text */
h1, h2, h3, p, sub, label {
    color: #f5f7fa !important; /* bright white */
    font-weight: 500;
}

/* Card styling */
.sim-card {
    background-color: #272b36; /* card background */
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #3b3f4d;
    margin-bottom: 25px;
}

/* Section headers inside cards */
.sim-card h3 {
    border-bottom: 2px solid #2ea043;
    padding-bottom: 5px;
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background-color: #238636;
    color: #ffffff;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    background-color: #2ea043;
}

/* Info boxes */
[data-testid="stInfo"] {
    background-color: #2b303a;
    border: 1px solid #3a3f4d;
}

/* Chat messages spacing */
[data-testid="stChatMessage"] {
    margin-bottom: 15px;
}

/* ======================
   Selectbox / Dropdown
   ====================== */

/* Container text (selected value) */
div.stSelectbox>div>div>div>div {
    color: #f5f7fa !important;  /* bright white */
}

/* Dropdown options */
div[role="listbox"] div[role="option"] {
    background-color: #272b36 !important; /* dark card background */
    color: #f5f7fa !important; /* readable text */
}

/* Hover effect in dropdown options */
div[role="listbox"] div[role="option"]:hover {
    background-color: #2ea043 !important; /* highlight on hover */
    color: #ffffff !important;
}

/* Input text fields */
div.stTextInput>div>div>input {
    color: #f5f7fa !important;
    background-color: #272b36 !important;
    border: 1px solid #3b3f4d;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 🏗 HEADER SECTION
# ============================================================

st.markdown("""
<div class="sim-card">
    <h1>🏗 Architecture Strategy Simulator</h1>
    <p>
    Think like a Senior Data Architect. Design. Defend. Optimize.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 🧠 SESSION STATE
# ============================================================

for key in ["setup_complete", "user_message_count",
            "feedback_shown", "chat_complete", "messages"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "messages" else []

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

# ============================================================
# 🔧 HELPER FUNCTIONS
# ============================================================

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

# ============================================================
# ⚙ SCENARIO SETUP
# ============================================================

if not st.session_state.setup_complete:

    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("⚙ Scenario Configuration")

    industry = st.selectbox("Industry",
                            ("E-commerce", "Healthcare", "FinTech", "Media", "Manufacturing"))

    company_size = st.selectbox("Company Size",
                                ("Startup", "Mid-size", "Enterprise"))

    cloud = st.selectbox("Cloud Provider",
                         ("AWS", "Azure", "GCP"))

    workload = st.selectbox("Primary Workload",
                            ("BI / Reporting", "Machine Learning",
                             "Real-time Streaming", "BI + ML"))

    budget = st.selectbox("Budget Sensitivity",
                          ("High (Cost sensitive)", "Medium",
                           "Low (Performance first)"))

    if st.button("Start Simulation"):
        st.session_state.industry = industry
        st.session_state.company_size = company_size
        st.session_state.cloud = cloud
        st.session_state.workload = workload
        st.session_state.budget = budget
        complete_setup()

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 🎯 SIMULATION PHASE
# ============================================================

if (st.session_state.setup_complete
    and not st.session_state.feedback_shown
    and not st.session_state.chat_complete):

    st.markdown("""
    <div class="sim-card">
        <h3>🎯 Simulation Active</h3>
        <p>
        You are the Data Architect. The AI is the CTO challenging your design.
        Consider scalability, cost, governance, and ML readiness.
        </p>
    </div>
    """, unsafe_allow_html=True)

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model_name = "gpt-4o-mini"

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": (
                f"You are the CTO of a {st.session_state.company_size} "
                f"{st.session_state.industry} company operating on {st.session_state.cloud}. "
                f"The company prioritizes {st.session_state.workload} workloads "
                f"and has {st.session_state.budget} budget sensitivity. "
                f"Describe a realistic business problem first. "
                f"Then ask the Data Architect to design the full data architecture. "
                f"After each answer, challenge their design with concerns about "
                f"cost, scalability, governance, compliance, reliability, and tradeoffs."
            )
        }]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.user_message_count < 6:

        if prompt := st.chat_input("Describe your architecture design...", max_chars=1500):

            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state.messages,
                    stream=True,
                )
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 6:
        st.session_state.chat_complete = True

# ============================================================
# 📊 FEEDBACK BUTTON
# ============================================================

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Architecture Evaluation"):
        show_feedback()

# ============================================================
# 📝 FEEDBACK SECTION
# ============================================================

if st.session_state.feedback_shown:

    st.markdown('<div class="sim-card">', unsafe_allow_html=True)
    st.subheader("📊 Architecture Evaluation")

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
You are a Senior Enterprise Data Architect evaluating a proposed architecture.

Score 1–10 based on:
- Scalability
- Cost efficiency
- Security & governance
- Cloud-native design
- ML readiness
- Tradeoff clarity

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
                "content": f"Evaluate this architecture discussion:\n{conversation_history}"
            }
        ]
    )

    st.write(feedback.choices[0].message.content)

    if st.button("Restart Simulation", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

    st.markdown('</div>', unsafe_allow_html=True)
