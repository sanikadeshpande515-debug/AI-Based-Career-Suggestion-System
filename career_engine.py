"""
career_engine.py
================
Rule-Based Inference Engine and Data Layer for AI-Based Career Suggestion System.

This module implements:
1. Data Layer: CSV knowledge base loading and option extraction.
2. Rule Base: Production rules (R1 to R6) with configurable weights.
3. Inference Engine: Input normalization, rule evaluation, weighted scoring,
   deterministic ranking, and human-readable explanation generation.

No Machine Learning, no neural networks, and no external black-box models.
Pure Knowledge-Driven Artificial Intelligence.
"""

import csv
import os
from typing import Dict, List, Any, Tuple, Optional

# ==============================================================================
# 1. RULE CONFIGURATION & WEIGHTS
# ==============================================================================

# Explicit rule weights defining the priority of each matching criterion
RULE_WEIGHTS = {
    "R1_SKILL": 3,        # Skill match is the primary indicator of technical capability
    "R2_INTEREST": 2,     # Passion and domain interest ensure career engagement
    "R3_SUBJECT": 2,      # Academic foundation relevant to the career discipline
    "R4_EDUCATION": 2,    # Baseline academic qualifications accepted
    "R5_WORK_STYLE": 1,   # Cultural, cognitive, and collaborative alignment
    "R6_EXPERIENCE": 1,   # Seniority and entry-level suitability
}

RULE_DEFINITIONS = [
    {
        "id": "R1",
        "name": "Skill Match",
        "weight": RULE_WEIGHTS["R1_SKILL"],
        "condition": "IF user's skill matches any required career skill",
        "reason_template": "Matched skills: {items}"
    },
    {
        "id": "R2",
        "name": "Interest Match",
        "weight": RULE_WEIGHTS["R2_INTEREST"],
        "condition": "IF user's interest matches career domain interests",
        "reason_template": "Matched interests: {items}"
    },
    {
        "id": "R3",
        "name": "Subject Match",
        "weight": RULE_WEIGHTS["R3_SUBJECT"],
        "condition": "IF user's strong subject matches relevant career subjects",
        "reason_template": "Matched subjects: {items}"
    },
    {
        "id": "R4",
        "name": "Education Match",
        "weight": RULE_WEIGHTS["R4_EDUCATION"],
        "condition": "IF user's degree/education is eligible for the career",
        "reason_template": "Education requirement satisfied ({degree})"
    },
    {
        "id": "R5",
        "name": "Work Style Match",
        "weight": RULE_WEIGHTS["R5_WORK_STYLE"],
        "condition": "IF user's work style matches career operational style",
        "reason_template": "Preferred work style matched ({style})"
    },
    {
        "id": "R6",
        "name": "Experience Match",
        "weight": RULE_WEIGHTS["R6_EXPERIENCE"],
        "condition": "IF user's seniority matches career recommended level",
        "reason_template": "Experience level matched ({level})"
    },
]

# Theoretical maximum score when all 6 rules fire successfully
MAX_POSSIBLE_SCORE = sum(RULE_WEIGHTS.values())  # 3 + 2 + 2 + 2 + 1 + 1 = 11


# ==============================================================================
# 2. DATA LAYER (CSV LOADER & OPTION EXTRACTOR)
# ==============================================================================

def load_careers(filepath: str = "careers.csv") -> List[Dict[str, Any]]:
    """
    Loads the career knowledge base from a CSV file.
    Parses semicolon-separated fields into clean, trimmed lists.
    """
    careers = []
    if not os.path.isabs(filepath):
        # Resolve relative to current file directory if relative
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_path = os.path.join(base_dir, filepath)
        if os.path.exists(candidate_path):
            filepath = candidate_path

    try:
        with open(filepath, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                career_record = {
                    "career": row["career"].strip(),
                    "description": row["description"].strip(),
                    "skills": [s.strip() for s in row["skills"].split(";") if s.strip()],
                    "interests": [i.strip() for i in row["interests"].split(";") if i.strip()],
                    "subjects": [sub.strip() for sub in row["subjects"].split(";") if sub.strip()],
                    "education": [e.strip() for e in row["education"].split(";") if e.strip()],
                    "work_style": [w.strip() for w in row["work_style"].split(";") if w.strip()],
                    "experience": [exp.strip() for exp in row["experience"].split(";") if exp.strip()],
                    "salary_range": row.get("salary_range", "N/A").strip(),
                    "growth": row.get("growth", "N/A").strip(),
                    "work_environment": row.get("work_environment", "N/A").strip(),
                }
                careers.append(career_record)
        return careers
    except FileNotFoundError:
        print(f"ERROR: Knowledge base file '{filepath}' not found.")
        return []
    except Exception as e:
        print(f"ERROR loading career database: {e}")
        return []


def get_options(careers: List[Dict[str, Any]], column: str) -> List[str]:
    """
    Extracts distinct sorted values from a given list/attribute column across all careers.
    Identical in design to get_options() from the reference project.
    """
    options_set = set()
    for career in careers:
        val = career.get(column, [])
        if isinstance(val, list):
            options_set.update(val)
        elif isinstance(val, str) and val:
            options_set.add(val)
    return sorted(list(options_set), key=lambda x: x.lower())


# ==============================================================================
# 3. INPUT VALIDATION MODULE
# ==============================================================================

def validate_user_profile(profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates user input before passing into the inference engine.
    Ensures mandatory fields have selections and values are appropriate.
    """
    errors = []
    
    # Check skills
    user_skills = profile.get("skills", [])
    if not user_skills or len(user_skills) == 0:
        errors.append("Please select at least one skill.")
        
    # Check interests
    user_interests = profile.get("interests", [])
    if not user_interests or len(user_interests) == 0:
        errors.append("Please select at least one area of interest.")
        
    # Check subjects
    user_subjects = profile.get("subjects", [])
    if not user_subjects or len(user_subjects) == 0:
        errors.append("Please select at least one favourite or strong subject.")
        
    # Check education
    education = profile.get("education", "").strip()
    if not education:
        errors.append("Please select your highest education level.")
        
    # Check work style
    work_style = profile.get("work_style")
    if not work_style:
        errors.append("Please specify your preferred work style.")
        
    # Check experience
    experience = profile.get("experience", "").strip()
    if not experience:
        errors.append("Please select your experience level.")
        
    is_valid = len(errors) == 0
    return is_valid, errors


# ==============================================================================
# 4. RULE-BASED SCORING & INFERENCE ENGINE
# ==============================================================================

def normalize_token(token: str) -> str:
    """Helper for case-insensitive and whitespace-tolerant comparisons."""
    return token.strip().lower()


def evaluate_career_rules(career: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates production rules R1 to R6 for a single career against user facts.
    Returns:
        - raw score
        - match percentage (0 to 100)
        - list of fired rules
        - human-readable explanation reasons
        - granular matched entities
    """
    score = 0
    reasons = []
    rules_fired = []

    # Prepare normalized career attribute sets
    career_skills_norm = {normalize_token(s): s for s in career["skills"]}
    career_interests_norm = {normalize_token(i): i for i in career["interests"]}
    career_subjects_norm = {normalize_token(sub): sub for sub in career["subjects"]}
    career_edu_norm = {normalize_token(e) for e in career["education"]}
    career_work_style_norm = {normalize_token(w): w for w in career["work_style"]}
    career_exp_norm = {normalize_token(exp) for exp in career["experience"]}

    # Prepare normalized user inputs
    user_skills = user_profile.get("skills", [])
    user_interests = user_profile.get("interests", [])
    user_subjects = user_profile.get("subjects", [])
    user_edu = normalize_token(user_profile.get("education", ""))
    user_work_styles = user_profile.get("work_style", [])
    if isinstance(user_work_styles, str):
        user_work_styles = [user_work_styles]
    user_exp = normalize_token(user_profile.get("experience", ""))

    # --- RULE 1: Skill Match (+3) ---
    matched_skills = []
    for s in user_skills:
        s_norm = normalize_token(s)
        if s_norm in career_skills_norm:
            matched_skills.append(career_skills_norm[s_norm])
    if matched_skills:
        score += RULE_WEIGHTS["R1_SKILL"]
        rules_fired.append("R1: Skill Match (+3)")
        reasons.append(f"✓ Skills matched ({len(matched_skills)}): {', '.join(matched_skills)}")

    # --- RULE 2: Interest Match (+2) ---
    matched_interests = []
    for i in user_interests:
        i_norm = normalize_token(i)
        if i_norm in career_interests_norm:
            matched_interests.append(career_interests_norm[i_norm])
    if matched_interests:
        score += RULE_WEIGHTS["R2_INTEREST"]
        rules_fired.append("R2: Interest Match (+2)")
        reasons.append(f"✓ Interests matched ({len(matched_interests)}): {', '.join(matched_interests)}")

    # --- RULE 3: Subject Match (+2) ---
    matched_subjects = []
    for sub in user_subjects:
        sub_norm = normalize_token(sub)
        if sub_norm in career_subjects_norm:
            matched_subjects.append(career_subjects_norm[sub_norm])
    if matched_subjects:
        score += RULE_WEIGHTS["R3_SUBJECT"]
        rules_fired.append("R3: Subject Match (+2)")
        reasons.append(f"✓ Strong subjects matched ({len(matched_subjects)}): {', '.join(matched_subjects)}")

    # --- RULE 4: Education Match (+2) ---
    education_matched = (user_edu in career_edu_norm) or ("other" in career_edu_norm)
    if education_matched:
        score += RULE_WEIGHTS["R4_EDUCATION"]
        rules_fired.append("R4: Education Match (+2)")
        reasons.append(f"✓ Education requirement satisfied ({user_profile.get('education')})")

    # --- RULE 5: Work Style Match (+1) ---
    matched_work_styles = []
    for ws in user_work_styles:
        ws_norm = normalize_token(ws)
        if ws_norm in career_work_style_norm:
            matched_work_styles.append(career_work_style_norm[ws_norm])
    if matched_work_styles:
        score += RULE_WEIGHTS["R5_WORK_STYLE"]
        rules_fired.append("R5: Work Style Match (+1)")
        reasons.append(f"✓ Preferred work style matches ({', '.join(matched_work_styles)})")

    # --- RULE 6: Experience Match (+1) ---
    experience_matched = (user_exp in career_exp_norm)
    if experience_matched:
        score += RULE_WEIGHTS["R6_EXPERIENCE"]
        rules_fired.append("R6: Experience Match (+1)")
        reasons.append(f"✓ Experience level matches ({user_profile.get('experience')})")

    # Calculate match percentage capped at 100%
    match_percentage = min(100, round((score / MAX_POSSIBLE_SCORE) * 100))

    return {
        "career": career["career"],
        "description": career["description"],
        "score": score,
        "max_score": MAX_POSSIBLE_SCORE,
        "match_percentage": match_percentage,
        "rules_fired": rules_fired,
        "reasons": reasons,
        "matched_skills": matched_skills,
        "matched_interests": matched_interests,
        "matched_subjects": matched_subjects,
        "matched_work_styles": matched_work_styles,
        "education_matched": education_matched,
        "experience_matched": experience_matched,
        "salary_range": career.get("salary_range", "N/A"),
        "growth": career.get("growth", "N/A"),
        "work_environment": career.get("work_environment", "N/A"),
        "all_required_skills": career["skills"],
        "all_interests": career["interests"],
    }


# ==============================================================================
# 5. RANKING & RECOMMENDATION DISPATCHER
# ==============================================================================

def recommend_careers(
    careers: List[Dict[str, Any]], 
    user_profile: Dict[str, Any], 
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Main recommendation function:
    1. Validates input
    2. Runs rule engine over all knowledge base records
    3. Retains candidates with score > 0
    4. Applies stable deterministic ranking:
       - Primary: Score descending
       - Secondary: Total count of matched skills descending
       - Tertiary: Total count of matched interests descending
       - Quaternary: Career name alphabetical ascending
    5. Returns top_n recommendations with full explanations.
    """
    recommendations = []

    for career in careers:
        eval_result = evaluate_career_rules(career, user_profile)
        if eval_result["score"] > 0:
            recommendations.append(eval_result)

    # Deterministic multi-key sorting
    recommendations.sort(
        key=lambda r: (
            -r["score"],
            -len(r["matched_skills"]),
            -len(r["matched_interests"]),
            r["career"]
        )
    )

    return recommendations[:top_n]


def get_rule_weight_table() -> List[Dict[str, Any]]:
    """
    Returns the transparent rule table for UI display and documentation.
    """
    return RULE_DEFINITIONS


# ==============================================================================
# 6. CONSOLE INTERFACE (MATCHING REFERENCE PROJECT ACADEMIC PATTERN)
# ==============================================================================

def display_options(title: str, options: List[str]) -> None:
    """Prints numbered/bulleted options to console."""
    print(f"\n{title}")
    for opt in options:
        print(f"  - {opt}")


def display_recommendations(recommendations: List[Dict[str, Any]]) -> None:
    """Formats and prints top recommendations with scores and explanations."""
    print("\n" + "=" * 75)
    print("                    TOP CAREER RECOMMENDATIONS")
    print("=" * 75)
    if not recommendations:
        print("\nNo matching careers found for your preference profile.")
        return

    for idx, rec in enumerate(recommendations, start=1):
        print(f"\n{idx}. {rec['career']}")
        print(f"   Match       : {rec['match_percentage']}% ({rec['score']}/{rec['max_score']} points)")
        print(f"   Description : {rec['description']}")
        print(f"   Compensation: {rec['salary_range']} | Market Growth: {rec['growth']}")
        print(f"   Environment : {rec['work_environment']}")
        print(f"   Rules Fired : {', '.join(rec['rules_fired'])}")
        print(f"   Explanations:")
        for r in rec["reasons"]:
            print(f"     {r}")
    print("\n" + "=" * 75)


def main():
    """
    Interactive Console Runner for Viva / Command-line demonstration.
    """
    print("=" * 75)
    print("           AI-BASED CAREER SUGGESTION SYSTEM (EXPERT SYSTEM)")
    print("=" * 75)
    print("\nWelcome! This system suggests careers using a transparent IF-THEN rule engine.")
    print("No machine learning or model training is used; all results are explainable.")

    careers = load_careers("careers.csv")
    if not careers:
        print("Failed to load knowledge base. Exiting.")
        return

    skills_opt = get_options(careers, "skills")
    interests_opt = get_options(careers, "interests")
    subjects_opt = get_options(careers, "subjects")

    while True:
        display_options("Available Sample Skills (comma-separated):", skills_opt[:10])
        skills_input = input("\nEnter your skills (comma-separated, e.g. Python, SQL): ").strip()
        user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]

        display_options("Available Sample Interests (comma-separated):", interests_opt[:10])
        interests_input = input("\nEnter your interests (comma-separated, e.g. Data, Technology): ").strip()
        user_interests = [i.strip() for i in interests_input.split(",") if i.strip()]

        display_options("Available Sample Subjects (comma-separated):", subjects_opt[:10])
        subjects_input = input("\nEnter strong subjects (comma-separated, e.g. Mathematics, Statistics): ").strip()
        user_subjects = [sub.strip() for sub in subjects_input.split(",") if sub.strip()]

        edu_input = input("\nEnter education (e.g. B.Tech, BCA, MCA, Diploma, Other) [Default: B.Tech]: ").strip()
        user_edu = edu_input if edu_input else "B.Tech"

        style_input = input("\nEnter work style (e.g. Analytical, Creative, Technical) [Default: Analytical]: ").strip()
        user_style = [s.strip() for s in style_input.split(",") if s.strip()] or ["Analytical"]

        exp_input = input("\nEnter experience (Beginner, Intermediate, Advanced) [Default: Beginner]: ").strip()
        user_exp = exp_input if exp_input else "Beginner"

        profile = {
            "skills": user_skills,
            "interests": user_interests,
            "subjects": user_subjects,
            "education": user_edu,
            "work_style": user_style,
            "experience": user_exp
        }

        is_valid, errors = validate_user_profile(profile)
        if not is_valid:
            print("\n[VALIDATION WARNINGS]:")
            for err in errors:
                print(f" - {err}")
            print("Please retry with valid selections.\n")
            continue

        recs = recommend_careers(careers, profile, top_n=5)
        display_recommendations(recs)

        again = input("\nDo you want another career assessment? (yes/no): ").strip().lower()
        if again != "yes":
            print("\nThank you for using the AI-Based Career Suggestion System!")
            break


if __name__ == "__main__":
    main()
