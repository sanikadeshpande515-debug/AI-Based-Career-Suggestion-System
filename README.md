# AI-Based Career Suggestion System

> **College Mini-Project | Artificial Intelligence Laboratory**  
> *A Knowledge-Driven, Rule-Based Expert System for Explainable Career Guidance*

---

> [!IMPORTANT]
> **Core Artificial Intelligence Principle:**  
> **This project uses a rule-based artificial intelligence approach and does not use machine learning.**  
> It relies entirely on a curated domain knowledge base, explicit IF–THEN production rules, weighted inference scoring, deterministic ranking, and human-readable explanation generation. There is no model training, no black-box neural network, and no external AI API dependency.

---

## 1. Abstract
Choosing a suitable career path is one of the most critical decisions faced by students in higher education. With the exponential growth of technology disciplines, students often experience information overload and cognitive fatigue when attempting to map their individual skill sets, academic strengths, and passions to the contemporary job market. This project presents the design and implementation of the **AI-Based Career Suggestion System**, a knowledge-driven artificial intelligence application developed using Python and Streamlit.

The system maintains a domain knowledge base of 20 realistic IT and engineering career profiles in a CSV file and evaluates user preferences using six predefined **IF–THEN production rules**. Each career candidate is scored through a weighted scoring engine: technical skills contribute three points (Rule R1), domain interests contribute two points (Rule R2), favourite academic subjects contribute two points (Rule R3), eligible education level contributes two points (Rule R4), preferred work style contributes one point (Rule R5), and experience level contributes one point (Rule R6), yielding a maximum possible score of 11 points (100% match).

Candidate careers are scored, ranked deterministically in descending order, and the **top 5 career recommendations** are presented with human-readable justifications detailing every satisfied rule and matching attribute. Comprehensive functional testing confirmed 100% test pass rate across valid inputs, empty selections, boundary qualifications, and reproducibility tests.

---

## 2. Introduction & Background

### 2.1 Background
Conventional career counselling platforms frequently suffer from one of two extremes:
1. **Static Category Listings:** Simple keyword search engines that fail to synthesize multidimensional aspects such as work style, academic strengths, and experience level together.
2. **Opaque Machine Learning Models:** Complex deep-learning recommenders that require massive historical user tracking data, suffer from the "cold-start" problem, and operate as unexplainable black boxes.

Rule-based expert systems—a cornerstone of classical Artificial Intelligence—encode human expert domain knowledge as structured **IF–THEN rules**. They provide complete transparency: the system can always explain precisely *why* a particular recommendation was reached.

### 2.2 Problem Statement
To design and implement an explainable, knowledge-driven Career Suggestion System that accepts a student's skills, interests, favourite academic subjects, education degree, preferred work style, and experience seniority, validates the inputs, applies a weighted rule base, and recommends the top five careers with granular explanations.

### 2.3 Objectives
- To study the principles of knowledge-driven artificial intelligence and rule-based expert systems.
- To design a weighted production rule base comprising skills, interests, subjects, education, work style, and experience rules.
- To separate application responsibilities into a strict **Three-Layer Architecture** (Presentation, Rule Engine, and Data Layer).
- To implement input validation, deterministic ranking, and an automated explanation generator.
- To build an interactive, responsive Streamlit web application.
- To validate the system through functional unit and black-box test cases.

---

## 3. System Architecture

The project adheres to a clean **Three-Layer Architecture** modeled after classical AI expert systems:

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER (UI)                 │
│  - Streamlit Web Application (app.py)                  │
│  - Multi-select controls, Dropdowns, Profile Presets   │
│  - Input validation alerts & warnings                  │
│  - Recommendation cards, Match % badges & Progress bars│
│  - Transparent Rule Matrix & Explanatory Pipeline      │
└───────────────────────────┬────────────────────────────┘
                            │ User facts / Profile dict
                            ▼
┌────────────────────────────────────────────────────────┐
│             RULE-BASED ENGINE LAYER                    │
│  - career_engine.py                                    │
│  - Production Rules R1 to R6 (Configurable Weights)    │
│  - Input Normalization (lowercase, trimmed whitespace) │
│  - Weighted Scoring Engine: Score(c) = Σ w_i * I_i     │
│  - Deterministic Ranking Module (Score -> Skills)      │
│  - Explanation Generator (Dynamically fired reasons)   │
└───────────────────────────┬────────────────────────────┘
                            │ Fetch career records
                            ▼
┌────────────────────────────────────────────────────────┐
│                     DATA LAYER                         │
│  - careers.csv (Domain Knowledge Base)                 │
│  - CSV Loader (DictReader / parse delimited fields)    │
│  - Option Extractor (get_options for dynamic UI)       │
└────────────────────────────────────────────────────────┘
```

---

## 4. Rule-Based AI Engine & Methodology

### 4.1 Production Rules and Weight Matrix

The inference engine evaluates six weighted production rules against each career in the knowledge base:

| Rule ID | Rule Name | Condition (IF) | Weight | Reason Generated |
|:---:|:---|:---|:---:|:---|
| **R1** | Skill Match | User's skill matches a career's required technical skill | **+3** | `✓ Skills matched (N): [Skill List]` |
| **R2** | Interest Match | User's interest matches career industry/domain area | **+2** | `✓ Interests matched (N): [Interest List]` |
| **R3** | Subject Match | User's strong subject matches relevant academic subjects | **+2** | `✓ Strong subjects matched (N): [Subject List]` |
| **R4** | Education Match | User's degree matches career eligible educational criteria | **+2** | `✓ Education requirement satisfied ([Degree])` |
| **R5** | Work Style Match | User's work style matches career operational style | **+1** | `✓ Preferred work style matches ([Style List])` |
| **R6** | Experience Match | User's seniority matches career recommended experience | **+1** | `✓ Experience level matches ([Level])` |

### 4.2 Scoring Formula & Match Percentage

For every career record $c$ and user input profile $U$:

$$\text{Score}(c) = \sum_{i=1}^{6} w_i \cdot I_i(c, U)$$

Where $I_i(c, U) \in \{0, 1\}$ is a binary indicator denoting whether Rule $R_i$ is satisfied.

- **Maximum Theoretical Score:**  
  $$\text{Score}_{\max} = 3 + 2 + 2 + 2 + 1 + 1 = 11 \text{ points}$$

- **Normalized Match Percentage:**  
  $$\text{Match Percentage}(c) = \min\left(100, \text{round}\left(\frac{\text{Score}(c)}{11} \times 100\right)\right)$$

### 4.3 Deterministic Ranking
To eliminate non-deterministic or arbitrary ordering when careers receive identical match scores, a multi-key sorting priority is enforced:
1. **Score** (Descending)
2. **Number of Matched Skills** (Descending)
3. **Number of Matched Interests** (Descending)
4. **Career Name** (Alphabetical Ascending)

This guarantees that identical inputs always produce the exact same ranked recommendations.

---

## 5. Dataset Description (`careers.csv`)

The knowledge base contains 20 comprehensive career profiles representing contemporary technology fields:

1. Software Developer
2. Web Developer
3. AI/ML Engineer
4. Data Scientist
5. Data Analyst
6. Cybersecurity Analyst
7. Cloud Engineer
8. DevOps Engineer
9. Blockchain Developer
10. UI/UX Designer
11. Product Manager
12. Business Analyst
13. Database Administrator
14. Mobile App Developer
15. Game Developer
16. Network Engineer
17. Embedded Systems Engineer
18. QA Automation Engineer
19. Information Security Officer
20. IT Systems Administrator

### Schema
- `career`: Title of the profession.
- `description`: Formal summary of the job role and core responsibilities.
- `skills`: Semicolon-delimited list of primary programming languages, tools, and technical competencies.
- `interests`: Semicolon-delimited industry domain interests.
- `subjects`: Semicolon-delimited foundational academic subjects.
- `education`: Semicolon-delimited accepted qualifications (`Diploma`, `BCA`, `B.Tech`, `B.E.`, `MCA`, `M.Tech`, `Other`).
- `work_style`: Semicolon-delimited preferred working traits (`Analytical`, `Creative`, `Technical`, `Collaborative`, `Independent`, `Leadership`, `Problem Solving`).
- `experience`: Semicolon-delimited experience tiers (`Beginner`, `Intermediate`, `Advanced`).
- `salary_range`: Indicative annual market compensation.
- `growth`: Projected employment growth rate.
- `work_environment`: Typical operating environment (e.g., Remote, Hybrid, Tech Office, SOC).

---

## 6. Project Structure

```
career-ai/
│
├── app.py                  # Presentation Layer: Streamlit interactive web application
├── career_engine.py        # Rule-Based AI Engine & Data Layer (production rules, scoring, ranking)
├── careers.csv             # Knowledge Base: 20 curated career records with rich metadata
├── test_career_engine.py   # Unit & Black-Box Test Suite (TC-01 through TC-10)
├── requirements.txt        # Minimal dependencies (streamlit, pandas)
└── README.md               # Comprehensive Academic Project Documentation
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### Step 1: Clone or Navigate to Project Directory
```powershell
cd C:\Users\Asus\.gemini\antigravity\scratch\career-ai
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Test Suite
Verify that all 10 academic test cases pass:
```powershell
python test_career_engine.py
```

### Step 4: Launch the Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 8. Example Execution Walkthrough

### Example Input
- **Skills:** Python, SQL, Problem Solving
- **Interests:** Data, Artificial Intelligence
- **Subjects:** Mathematics, Statistics
- **Education:** B.Tech
- **Work Style:** Analytical, Problem Solving
- **Experience:** Beginner

### Example Output
```
1. Data Scientist
   Match: 100% (11 / 11 pts)
   Description: Extracts predictive insights from structured and unstructured data using mathematical and statistical methods.
   Rules Fired: [R1: Skill Match, R2: Interest Match, R3: Subject Match, R4: Education Match, R5: Work Style Match, R6: Experience Match]
   Why this matches you:
   ✓ Skills matched (3): Python, SQL, Problem Solving
   ✓ Interests matched (2): Data, Artificial Intelligence
   ✓ Strong subjects matched (2): Mathematics, Statistics
   ✓ Education requirement satisfied (B.Tech)
   ✓ Preferred work style matches (Analytical, Problem Solving)
   ✓ Experience level matches (Beginner)
   Salary: INR 8.5 - 20 LPA | Growth: Very High (28% growth) | Environment: Corporate Analytics / Hybrid

2. Data Analyst
   Match: 91% (10 / 11 pts)
   Description: Cleans, transforms, and visualizes company data to aid strategic decision making and reporting.
   ...
```

---

## 9. Test Verification (TC-01 to TC-10)

| Test Case | Scenario Tested | Input Values | Expected Result | Status |
|:---:|:---|:---|:---|:---:|
| **TC-01** | Valid Profile (Data Scientist) | Python, SQL, Math, Stats, B.Tech | Data Scientist ranked #1 with 100% score | **PASS** |
| **TC-02** | Input Validation (Empty Skills) | No skills selected | Validation error triggered, rejection without crash | **PASS** |
| **TC-03** | Multiple Skills (Web Dev) | JavaScript, HTML, CSS, Git | Web Developer ranked #1 | **PASS** |
| **TC-04** | Security Interest Bias | Networking, Linux, Cybersecurity | Cybersecurity Analyst placed in top recommendations | **PASS** |
| **TC-05** | Alternative Education | Non-engineering degree (Other/BCA) | UI/UX Designer properly satisfies education rule | **PASS** |
| **TC-06** | Management Work Style | Leadership, Communication, Business | Product Manager / Business Analyst prioritized | **PASS** |
| **TC-07** | Beginner Level Suitability | Beginner seniority, foundational skills | Beginner-accepting careers correctly matched | **PASS** |
| **TC-08** | Advanced Seniority | Solidity, Blockchain, Advanced | Blockchain Developer placed top with full score | **PASS** |
| **TC-09** | Determinism & Stability | Repeated runs of identical profile | 100% identical score, ranking, and order | **PASS** |
| **TC-10** | Profile Divergence | Creative designer vs technical coder | Completely distinct top recommendations produced | **PASS** |

---

## 10. Advantages and Limitations

### Advantages
1. **Full Explainability:** Every recommendation details the exact production rules that fired and lists matching entities.
2. **Zero Training Data Needed:** Operates instantly from first principles without requiring user tracking logs or massive datasets.
3. **Deterministic & Reproducible:** Identical inputs yield identical rankings every single time.
4. **Computational Efficiency:** Evaluation takes less than 5 milliseconds ($O(N \cdot K)$ time complexity).
5. **Easily Extensible Knowledge Base:** New careers or emerging skills can be added directly to `careers.csv` without modifying the core inference code.

### Limitations
1. **Static Knowledge Base:** Does not automatically discover emerging industry roles without updating `careers.csv`.
2. **Discrete Matching:** Relies on discrete keyword taxonomy rather than semantic sentence interpretation.
3. **No Dynamic Weight Tuning:** Rule weights are pre-configured rather than learned from user feedback.

---

## 11. Future Scope
- **NLP Resume Parser:** Integrating text extraction to automatically extract skills from uploaded PDF/Word resumes.
- **Skill Gap Analysis:** Highlighting missing skills between a student's profile and their dream career, recommending tailored certification courses.
- **Dynamic Job Market Integration:** Pulling real-time hiring trends and opening counts from employment APIs.
- **Hybrid Recommender System:** Augmenting rule-based inference with collaborative filtering once a large base of historical student feedback is collected.

---

## 12. References
1. Hayes-Roth, F., Waterman, D. A., & Lenat, D. B. (1983). *Building Expert Systems*. Addison-Wesley.
2. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
3. Resnick, P., & Varian, H. R. (1997). Recommender systems. *Communications of the ACM*, 40(3), 56–58.
4. Pazzani, M. J., & Billsus, D. (2007). Content-based recommendation systems. In *The Adaptive Web* (pp. 325–341). Springer.
5. Burke, R. (2002). Hybrid recommender systems: Survey and experiments. *User Modeling and User-Adapted Interaction*, 12(4), 331–370.
