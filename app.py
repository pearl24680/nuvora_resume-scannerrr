import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt
from openai import OpenAI

# ==============================
# 🔑 OPENAI CLIENT
# ==============================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==============================
# 🎨 PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="💫 Nuvora Resume Scanner",
    page_icon="💼",
    layout="wide"
)

# ==============================
# 🎨 CUSTOM CSS
# ==============================
st.markdown("""
<style>
body, .stApp {
    background-color: #0A0F24;
    color: #EAEAEA;
    font-family: 'Poppins', sans-serif;
}
.title {
    font-size: 40px;
    font-weight: 800;
    background: linear-gradient(90deg, #00C6FF, #0072FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}
.card {
    background: #13193B;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.mini-card {
    background: #1B1F3B;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.stButton>button {
    background: linear-gradient(90deg, #0072FF, #00C6FF);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 📂 FILE FUNCTIONS
# ==============================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    return ""

def calculate_ats_score(resume, jd):
    resume_words = set(re.findall(r"\b\w+\b", resume.lower()))
    jd_words = set(re.findall(r"\b\w+\b", jd.lower()))
    matched = resume_words & jd_words
    missing = jd_words - resume_words
    score = (len(matched) / len(jd_words)) * 100 if jd_words else 0
    return round(score, 2), matched, missing

# ==============================
# 🤖 AI CHAT FUNCTION
# ==============================
def ai_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Nuvora AI, a helpful career and resume assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )
    return response.choices[0].message.content

# ==============================
# 🧭 SIDEBAR
# ==============================
st.sidebar.title("💫 Nuvora AI")
page = st.sidebar.radio("Navigate", ["🏠 Home", "📊 Resume Scanner", "💬 Chat Assistant"])
st.sidebar.caption("Developed by Pearl & Vasu")

# ==============================
# 🏠 HOME
# ==============================
if page == "🏠 Home":
    st.markdown("<p class='title'>Nuvora Resume Intelligence</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
    <h3>🚀 Features</h3>
    <ul>
        <li>ATS Resume Scoring</li>
        <li>Skill Match Analysis</li>
        <li>AI Career Chatbot</li>
        <li>Job Description Comparison</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 RESUME SCANNER
# ==============================
elif page == "📊 Resume Scanner":
    st.markdown("<p class='title'>Resume Analyzer</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", ["pdf", "docx"])

    with col2:
        jd_option = st.selectbox(
            "Select Job Description",
            ["Data Scientist", "Web Developer", "AI Engineer", "Software Developer"]
        )

    jd_presets = {
        "Data Scientist": "python pandas numpy machine learning sql data visualization statistics",
        "Web Developer": "html css javascript react node api git",
        "AI Engineer": "python tensorflow pytorch nlp deep learning",
        "Software Developer": "java c++ data structures algorithms databases"
    }

    if resume_file:
        resume_text = extract_text(resume_file)
        jd_text = jd_presets[jd_option]

        score, matched, missing = calculate_ats_score(resume_text, jd_text)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='mini-card'><h2>{score}%</h2><p>ATS Score</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='mini-card'><h2>{len(matched)}</h2><p>Matched</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='mini-card'><h2>{len(missing)}</h2><p>Missing</p></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'><h4>Missing Skills</h4>", unsafe_allow_html=True)
        st.write(", ".join(list(missing)) if missing else "Perfect match 🎉")
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# 💬 CHAT ASSISTANT
# ==============================
elif page == "💬 Chat Assistant":
    st.markdown("<p class='title'>Nuvora AI Chat</p>", unsafe_allow_html=True)

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.text_input("Ask about resume, skills, interview...")

    if user_input:
        st.session_state.chat.append(("You", user_input))
        with st.spinner("Nuvora is thinking 💫"):
            reply = ai_chat(user_input)
        st.session_state.chat.append(("Nuvora 💫", reply))

    for sender, msg in st.session_state.chat:
        st.markdown(f"<div class='card'><b>{sender}</b><br>{msg}</div>", unsafe_allow_html=True)

# ==============================
# 🧾 FOOTER
# ==============================
st.markdown("<hr><p style='text-align:center;color:gray;'>Made with ❤️ by Pearl & Vasu</p>", unsafe_allow_html=True)
