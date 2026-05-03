import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval
from pinecone import Pinecone, ServerlessSpec
import uuid
import sqlite3
import json

# ============================================================
# SQLITE (SYSTEM OF RECORD)
# ============================================================

conn = sqlite3.connect("projects.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    project_name TEXT,
    business_process TEXT,
    grain TEXT,
    source_tables TEXT,
    kpis TEXT,
    ai_response TEXT
)
""")
conn.commit()

# ============================================================
# PINECONE (VECTOR SEARCH ONLY)
# ============================================================

def get_pinecone_index():

    pinecone_key = st.secrets.get("PINECONE_API_KEY")

    if not pinecone_key:
        st.error("Missing PINECONE_API_KEY in Streamlit Secrets")
        st.stop()

    pc = Pinecone(api_key=pinecone_key)

    INDEX_NAME = "data-architect-projects"

    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    return pc.Index(INDEX_NAME)

index = get_pinecone_index()

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "setup_complete": False,
    "ai_response": ""
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# AUTH
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
#  HELPERS
# ============================================================

def get_embedding(text):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding


def build_text(bp, grain, tables, kpis):
    return f"""
Business Process: {bp}
Grain: {grain}
Source Tables: {tables}
KPIs: {kpis}
"""

# ============================================================
# SAVE PROJECT (SQLITE + PINECONE)
# ============================================================

def save_project(name, bp, grain, tables, kpis, ai_response):

    project_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        name,
        bp,
        grain,
        tables,
        kpis,
        ai_response
    ))
    conn.commit()

    embedding = get_embedding(build_text(bp, grain, tables, kpis))

    index.upsert([
        (project_id, embedding, {
            "project_name": name,
            "business_process": bp,
            "grain": grain,
            "source_tables": tables,
            "kpis": kpis,
            "ai_response": ai_response
        })
    ])

# ============================================================
# LOAD PROJECT (TRUE RESUME = SQLITE)
# ============================================================

def load_project(project_name):

    cursor.execute("""
        SELECT * FROM projects WHERE project_name = ?
    """, (project_name,))

    row = cursor.fetchone()

    if row:
        return {
            "id": row[0],
            "project_name": row[1],
            "business_process": row[2],
            "grain": row[3],
            "source_tables": row[4],
            "kpis": row[5],
            "ai_response": row[6]
        }

    return None

# ============================================================
#  SEMANTIC SEARCH (PINECONE)
# ============================================================

def search_projects(query):

    embedding = get_embedding(query)

    results = index.query(
        vector=embedding,
        top_k=5,
        include_metadata=True
    )

    return results.get("matches", [])

# ============================================================
# ⚙ SETUP
# ============================================================

if not st.session_state.setup_complete:

    st.subheader("⚙ Model Setup")

    business_process = st.text_area(
        "Business Process",
        placeholder="Example: Students use meal cards at campus food locations..."
    )

    grain = st.text_input(
        "Grain",
        placeholder="Example: One row per student per food location per day"
    )

    source_tables = st.text_area(
        "Source Tables",
        placeholder="Example: Student, Campus_Food, Meal_Card_Transactions..."
    )

    kpis = st.text_area(
        "KPIs",
        placeholder="Example: Daily balance, total spend, number of swipes..."
    )

    if st.button("Start Modeling"):
        st.session_state.business_process = business_process
        st.session_state.grain = grain
        st.session_state.source_tables = source_tables
        st.session_state.kpis = kpis
        st.session_state.setup_complete = True

# ============================================================
# MEMORY MODE (RAG)
# ============================================================

memory_mode = st.checkbox("Memory Mode (RAG)")

# ============================================================
# MODEL GENERATION
# ============================================================

if st.session_state.setup_complete:

    if not st.session_state.ai_response:

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        memory_context = ""

        if memory_mode:
            matches = search_projects(st.session_state.business_process)

            for m in matches:
                meta = m["metadata"]
                memory_context += f"""
Project: {meta['project_name']}
Process: {meta['business_process']}
Grain: {meta['grain']}
KPIs: {meta['kpis']}
---
"""

        prompt = f"""
You are a Principal Data Architect.

{memory_context if memory_context else "Fresh Mode: no past context used."}

Business Process: {st.session_state.business_process}
Grain: {st.session_state.grain}
Source Tables: {st.session_state.source_tables}
KPIs: {st.session_state.kpis}

Design a dimensional model.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.session_state.ai_response = response.choices[0].message.content

    st.subheader("📊 Output")
    st.write(st.session_state.ai_response)

# ============================================================
# SAVE UI
# ============================================================

project_name = st.text_input("Save project name")

if st.button("Save Project"):
    save_project(
        project_name,
        st.session_state.business_process,
        st.session_state.grain,
        st.session_state.source_tables,
        st.session_state.kpis,
        st.session_state.ai_response
    )
    st.success("Saved to SQLite + indexed in Pinecone!")

# ============================================================
# RESUME PROJECT (REAL MEMORY = SQLITE)
# ============================================================

st.subheader("📂 Resume Project")

cursor.execute("SELECT project_name FROM projects")
projects = [r[0] for r in cursor.fetchall()]

selected = st.selectbox("Select project", projects)

if st.button("Load Project"):

    proj = load_project(selected)

    if proj:

        st.session_state.business_process = proj["business_process"]
        st.session_state.grain = proj["grain"]
        st.session_state.source_tables = proj["source_tables"]
        st.session_state.kpis = proj["kpis"]
        st.session_state.ai_response = proj["ai_response"]

        st.session_state.setup_complete = True

        st.rerun()

# ============================================================
#  SEMANTIC SEARCH (OPTIONAL)
# ============================================================

search_query = st.text_input("Semantic search projects")

if st.button("Search Similar Projects"):
    results = search_projects(search_query)

    for r in results:
        st.write(f"**{r['metadata']['project_name']}**")