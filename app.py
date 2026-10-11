"""
app.py
======
Presentation Layer: Streamlit Web Application for AI-Based Career Suggestion System.

Architecture:
  Layer 1: Presentation Layer (Streamlit UI, form controls, validation display, recommendation cards)
  Layer 2: Rule-Based Engine Layer (career_engine.py: inference, weighted scoring, explanation generator)
  Layer 3: Data Layer (careers.csv knowledge base)
"""

import streamlit as st
import pandas as pd
from career_engine import (
    load_careers,
    get_options,
    validate_user_profile,
    recommend_careers,
    get_rule_weight_table,
    MAX_POSSIBLE_SCORE,
    RULE_WEIGHTS,
)

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Based Career Suggestion System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic, polished, professional look
st.markdown("""
<style>
    /* Global accents and typography */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }
    .career-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 6px solid #2563EB;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .career-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .match-pill {
        display: inline-block;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.95rem;
    }
    .match-high {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #84E1BC;
    }
    .match-med {
        background-color: #FEF08A;
        color: #713F12;
        border: 1px solid #FACC15;
    }
    .match-low {
        background-color: #F3F4F6;
        color: #374151;
        border: 1px solid #D1D5DB;
    }
    .rule-tag {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 2px 8px;
        margin-right: 6px;
        margin-top: 4px;
    }
    .pipeline-step {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 600;
        color: #1E293B;
    }
    .reason-list {
        margin-top: 8px;
        margin-bottom: 12px;
        padding-left: 18px;
        color: #374151;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .metric-chip {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. LOAD KNOWLEDGE BASE & EXTRACT OPTIONS
# ------------------------------------------------------------------------------
@st.cache_data
def get_cached_careers():
    return load_careers("careers.csv")

careers = get_cached_careers()

if not careers:
    st.error("Knowledge base could not be loaded. Please ensure `careers.csv` is present in the project directory.")
    st.stop()

# Extract unique option lists from knowledge base
available_skills = get_options(careers, "skills")
available_interests = get_options(careers, "interests")
available_subjects = get_options(careers, "subjects")
available_work_styles = get_options(careers, "work_style")
available_education = ["Diploma", "BCA", "B.Tech", "B.E.", "MCA", "M.Tech", "Other"]
available_experience = ["Beginner", "Intermediate", "Advanced"]

# ------------------------------------------------------------------------------
# 3. SIDEBAR: NAVIGATION & ACADEMIC DOCUMENTATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 Academic Project Info")
    st.markdown("""
    **Project Title:**  
    AI-Based Career Suggestion System
    
    **AI Paradigm:**  
    Knowledge-Driven / Production Rule System
    
    **Inference Method:**  
    Weighted IF–THEN Scoring Engine
    
    **Architecture:**  
    Three-Tier Layered Architecture:
    1. Presentation Layer (Streamlit)
    2. Rule Engine Layer (Production Rules R1–R6)
    3. Data Layer (careers.csv)
    """)
    st.divider()

    st.markdown("### ⚖️ Rule Weight Matrix")
    rule_table = get_rule_weight_table()
    df_rules = pd.DataFrame([
        {"Rule": r["id"], "Name": r["name"], "Weight": f"+{r['weight']} pts"}
        for r in rule_table
    ])
    st.dataframe(df_rules, hide_index=True, use_container_width=True)
    st.caption(f"**Max Theoretical Score:** {MAX_POSSIBLE_SCORE} Points = 100%")
    st.divider()

    st.markdown("### ⚙️ Quick Profile Presets")
    preset_choice = st.selectbox(
        "Load Sample Student Persona:",
        ["None (Custom Profile)", "Data Science Aspirant", "Web & Frontend Enthusiast", "Cybersecurity Specialist", "Product & Business Leader"]
    )

# Manage Preset Defaults
default_skills = []
default_interests = []
default_subjects = []
default_edu = "B.Tech"
default_styles = ["Analytical", "Problem Solving"]
default_exp = "Beginner"

if preset_choice == "Data Science Aspirant":
    default_skills = ["Python", "SQL", "Problem Solving"]
    default_interests = ["Data", "Artificial Intelligence"]
    default_subjects = ["Mathematics", "Statistics"]
    default_edu = "B.Tech"
    default_styles = ["Analytical", "Problem Solving"]
    default_exp = "Beginner"
elif preset_choice == "Web & Frontend Enthusiast":
    default_skills = ["JavaScript", "HTML", "CSS", "Git"]
    default_interests = ["Web Development", "Technology"]
    default_subjects = ["Computer Science", "English"]
    default_edu = "BCA"
    default_styles = ["Creative", "Technical"]
    default_exp = "Beginner"
elif preset_choice == "Cybersecurity Specialist":
    default_skills = ["Networking", "Linux", "Problem Solving"]
    default_interests = ["Cybersecurity", "Technology"]
    default_subjects = ["Computer Science", "Physics"]
    default_edu = "B.Tech"
    default_styles = ["Technical", "Independent"]
    default_exp = "Intermediate"
elif preset_choice == "Product & Business Leader":
    default_skills = ["Leadership", "Communication", "Data Analysis", "Problem Solving"]
    default_interests = ["Business", "Management"]
    default_subjects = ["Business Studies", "Economics"]
    default_edu = "B.Tech"
    default_styles = ["Leadership", "Collaborative"]
    default_exp = "Intermediate"

# ------------------------------------------------------------------------------
# 4. HEADER SECTION
# ------------------------------------------------------------------------------
st.markdown('<div class="ai-badge">⚡ KNOWLEDGE-DRIVEN AI ENGINE • DETERMINISTIC & EXPLAINABLE</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">AI-Based Career Suggestion System</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover ideal career paths matching your skills, academic strengths, and career preferences using transparent rule-based reasoning.</p>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. INPUT FORM (PRESENTATION LAYER)
# ------------------------------------------------------------------------------
st.markdown("### 📋 Student Profile Assessment")
st.write("Fill in your details below. The rule-based engine will evaluate each profile attribute against the career knowledge base.")

with st.form("career_assessment_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**1. Technical & Professional Skills**")
        selected_skills = st.multiselect(
            "Select skills you currently know or are studying:",
            options=available_skills,
            default=[s for s in default_skills if s in available_skills],
            placeholder="Select one or more skills (e.g., Python, SQL, Git...)",
            help="Rule R1 evaluates skill overlap against career core technical prerequisites."
        )

        st.markdown("**2. Domain Interests & Passions**")
        selected_interests = st.multiselect(
            "Select technology & industry domains that interest you:",
            options=available_interests,
            default=[i for i in default_interests if i in available_interests],
            placeholder="Select interest fields (e.g., Artificial Intelligence, Cybersecurity...)",
            help="Rule R2 matches your personal excitement with career domains."
        )

        st.markdown("**3. Strong or Favourite Subjects**")
        selected_subjects = st.multiselect(
            "Select academic subjects in which you feel confident:",
            options=available_subjects,
            default=[sub for sub in default_subjects if sub in available_subjects],
            placeholder="Select subjects (e.g., Mathematics, Computer Science...)",
            help="Rule R3 verifies foundational curriculum relevance."
        )

    with col2:
        st.markdown("**4. Education Level**")
        edu_index = available_education.index(default_edu) if default_edu in available_education else 2
        selected_education = st.selectbox(
            "Your highest current or completed degree:",
            options=available_education,
            index=edu_index,
            help="Rule R4 matches formal degree criteria required by hiring standards."
        )

        st.markdown("**5. Preferred Work Style**")
        selected_work_styles = st.multiselect(
            "How do you prefer to operate on a daily basis?",
            options=available_work_styles,
            default=[w for w in default_styles if w in available_work_styles],
            placeholder="Choose work styles (e.g., Analytical, Collaborative, Creative...)",
            help="Rule R5 evaluates cognitive, behavioral, and team dynamics."
        )

        st.markdown("**6. Experience Level**")
        exp_index = available_experience.index(default_exp) if default_exp in available_experience else 0
        selected_experience = st.selectbox(
            "Your professional or project experience seniority:",
            options=available_experience,
            index=exp_index,
            help="Rule R6 ensures entry-level vs senior expectations match."
        )

    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 4])
    with btn_col1:
        submit_btn = st.form_submit_button("🚀 Find My Career", type="primary", use_container_width=True)
    with btn_col2:
        clear_btn = st.form_submit_button("🔄 Reset Profile", use_container_width=True)

if clear_btn:
    st.rerun()

# ------------------------------------------------------------------------------
# 6. INFERENCE & RECOMMENDATIONS (RULE ENGINE LAYER)
# ------------------------------------------------------------------------------
if submit_btn:
    user_profile = {
        "skills": selected_skills,
        "interests": selected_interests,
        "subjects": selected_subjects,
        "education": selected_education,
        "work_style": selected_work_styles,
        "experience": selected_experience,
    }

    # Step 1: Input Validation
    is_valid, validation_errors = validate_user_profile(user_profile)

    if not is_valid:
        st.error("⚠️ **Validation Notice:** Please address the following requirements to ensure accurate recommendations:")
        for err in validation_errors:
            st.markdown(f"- {err}")
    else:
        # Step 2: Rule-based inference & deterministic ranking
        top_recommendations = recommend_careers(careers, user_profile, top_n=5)

        st.divider()
        st.markdown("## 🎯 Top Career Matches & Explanations")
        st.caption(f"Showing the top {len(top_recommendations)} career paths sorted by rule match score and deterministic priority.")

        if not top_recommendations:
            st.warning("No matching careers found for the given criteria. Try broadening your skill or interest selections.")
        else:
            for idx, rec in enumerate(top_recommendations, start=1):
                match_pct = rec["match_percentage"]
                
                # Determine badge styling
                if match_pct >= 80:
                    badge_class = "match-high"
                elif match_pct >= 50:
                    badge_class = "match-med"
                else:
                    badge_class = "match-low"

                with st.container(border=True):
                    header_left, header_right = st.columns([3, 1.2])
                    with header_left:
                        st.markdown(f"<h3 style='margin: 0; color: #1E3A8A;'>#{idx} {rec['career']}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #4B5563; margin-top: 4px; font-size: 1rem;'>{rec['description']}</p>", unsafe_allow_html=True)
                    with header_right:
                        st.markdown(f"""
                        <div style="text-align: right; margin-top: 4px;">
                            <span class="match-pill {badge_class}">{match_pct}% Match</span><br>
                            <span style="font-size: 0.85rem; color: #6B7280; font-weight: 600;">{rec['score']} of {rec['max_score']} points</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Streamlit visual progress bar
                    st.progress(match_pct / 100.0)

                    # Rules fired tags
                    st.markdown("**Rules Satisfied:**")
                    rule_tags_html = "".join([f'<span class="rule-tag">{r}</span>' for r in rec['rules_fired']])
                    st.markdown(f"<div style='margin-bottom: 12px;'>{rule_tags_html}</div>", unsafe_allow_html=True)

                    # Explainability section
                    st.markdown("**Why this career matches your profile:**")
                    for reason in rec["reasons"]:
                        st.markdown(f"- {reason}")

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                    # Additional career insights via clean metrics
                    c_col1, c_col2, c_col3 = st.columns(3)
                    with c_col1:
                        st.metric(label="Estimated Compensation", value=rec['salary_range'])
                    with c_col2:
                        st.metric(label="Industry Growth", value=rec['growth'])
                    with c_col3:
                        st.metric(label="Work Environment", value=rec['work_environment'])

# ------------------------------------------------------------------------------
# 7. HOW THE AI WORKS SECTION (EXPLANATORY PIPELINE)
# ------------------------------------------------------------------------------
st.divider()
st.markdown("## 🧠 How the Rule-Based AI Engine Operates")
st.markdown("""
Unlike statistical black-box models, this system is an **Expert System** implementing knowledge-driven artificial intelligence.
Every career recommendation is fully auditable, deterministic, and traceable back to formal production rules.
""")

p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)
with p_col1:
    st.markdown("""
    <div class="pipeline-step">
        1. User Input<br>
        <small style="color: #64748B;">Skills, Interests, Subjects, Education</small>
    </div>
    """, unsafe_allow_html=True)
with p_col2:
    st.markdown("""
    <div class="pipeline-step">
        2. Validation<br>
        <small style="color: #64748B;">Case normalisation & boundary checks</small>
    </div>
    """, unsafe_allow_html=True)
with p_col3:
    st.markdown("""
    <div class="pipeline-step">
        3. Rule Firing<br>
        <small style="color: #64748B;">Evaluate R1–R6 against Knowledge Base</small>
    </div>
    """, unsafe_allow_html=True)
with p_col4:
    st.markdown("""
    <div class="pipeline-step">
        4. Scoring & Rank<br>
        <small style="color: #64748B;">Weighted sum & deterministic sorting</small>
    </div>
    """, unsafe_allow_html=True)
with p_col5:
    st.markdown("""
    <div class="pipeline-step">
        5. Explanations<br>
        <small style="color: #64748B;">Top 5 results with human-readable reasons</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("🔍 Mathematical Formulation & Production Rule Details", expanded=False):
    st.markdown(r"""
    The inference engine evaluates each career record $c$ against user preference facts $U$ using an additive linear scoring function:
    
    $$Score(c) = \sum_{i=1}^{6} w_i \cdot I_i(c, U)$$
    
    Where:
    - $w_1 = 3$ for **R1 (Skill Match)**: $I_1 = 1$ if $\text{skills}(U) \cap \text{skills}(c) \neq \emptyset$, else $0$.
    - $w_2 = 2$ for **R2 (Interest Match)**: $I_2 = 1$ if $\text{interests}(U) \cap \text{interests}(c) \neq \emptyset$, else $0$.
    - $w_3 = 2$ for **R3 (Subject Match)**: $I_3 = 1$ if $\text{subjects}(U) \cap \text{subjects}(c) \neq \emptyset$, else $0$.
    - $w_4 = 2$ for **R4 (Education Match)**: $I_4 = 1$ if $\text{education}(U) \in \text{education}(c)$, else $0$.
    - $w_5 = 1$ for **R5 (Work Style Match)**: $I_5 = 1$ if $\text{work\_style}(U) \cap \text{work\_style}(c) \neq \emptyset$, else $0$.
    - $w_6 = 1$ for **R6 (Experience Match)**: $I_6 = 1$ if $\text{experience}(U) \in \text{experience}(c)$, else $0$.
    
    The maximum obtainable score is:
    $$Score_{\max} = 3 + 2 + 2 + 2 + 1 + 1 = 11$$
    
    The normalized match percentage is calculated as:
    $$MatchPercentage(c) = \min\left(100, \text{round}\left(\frac{Score(c)}{11} \times 100\right)\right)$$
    """)

# ------------------------------------------------------------------------------
# 8. FOOTER / ABOUT THE PROJECT
# ------------------------------------------------------------------------------
st.divider()
f_col1, f_col2 = st.columns([3, 1])
with f_col1:
    st.markdown("""
    **AI Laboratory College Mini-Project**  
    *Designed and developed following the Knowledge-Based Expert System paradigm.*  
    No Machine Learning • Deterministic Reasoning • 100% Explainable Recommendations
    """)
with f_col2:
    st.caption("College Mini Project © 2026-2027")
