"""
test_career_engine.py
=====================
Functional black-box and unit tests for the Rule-Based Career Suggestion System.
Inspired by the functional test cases (TC-01 through TC-07) in the reference project.
"""

import unittest
from career_engine import (
    load_careers,
    get_options,
    validate_user_profile,
    evaluate_career_rules,
    recommend_careers,
    MAX_POSSIBLE_SCORE
)

class TestCareerEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load careers from careers.csv
        cls.careers = load_careers("careers.csv")
        assert len(cls.careers) >= 15, f"Knowledge base should have at least 15 careers, found {len(cls.careers)}"

    def test_tc01_valid_input_data_scientist(self):
        """TC-01: Valid user query targeting Data Scientist profile."""
        profile = {
            "skills": ["Python", "SQL", "Problem Solving"],
            "interests": ["Data", "Artificial Intelligence"],
            "subjects": ["Mathematics", "Statistics"],
            "education": "B.Tech",
            "work_style": ["Analytical", "Problem Solving"],
            "experience": "Intermediate"
        }
        is_valid, errors = validate_user_profile(profile)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        results = recommend_careers(self.careers, profile, top_n=5)
        self.assertGreater(len(results), 0)
        top_career = results[0]
        self.assertIn(top_career["career"], ["Data Scientist", "AI/ML Engineer"])
        self.assertEqual(top_career["score"], 11)  # All 6 rules fired
        self.assertEqual(top_career["match_percentage"], 100)
        self.assertEqual(len(top_career["rules_fired"]), 6)

    def test_tc02_no_skills_validation(self):
        """TC-02: Input validation should reject empty skills."""
        profile = {
            "skills": [],
            "interests": ["Programming"],
            "subjects": ["Computer Science"],
            "education": "BCA",
            "work_style": ["Technical"],
            "experience": "Beginner"
        }
        is_valid, errors = validate_user_profile(profile)
        self.assertFalse(is_valid)
        self.assertTrue(any("skill" in err.lower() for err in errors))

    def test_tc03_multiple_skills_web_developer(self):
        """TC-03: Multiple matching front-end skills correctly favor Web Developer."""
        profile = {
            "skills": ["JavaScript", "HTML", "CSS", "Git"],
            "interests": ["Web Development", "Technology"],
            "subjects": ["Computer Science"],
            "education": "Diploma",
            "work_style": ["Creative"],
            "experience": "Beginner"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        top_career = results[0]
        self.assertEqual(top_career["career"], "Web Developer")
        self.assertEqual(top_career["score"], 11)
        self.assertIn("R1: Skill Match (+3)", top_career["rules_fired"])
        self.assertIn("R2: Interest Match (+2)", top_career["rules_fired"])

    def test_tc04_different_interests_cybersecurity(self):
        """TC-04: Domain interest in Cybersecurity drives security roles to top."""
        profile = {
            "skills": ["Networking", "Linux", "Problem Solving"],
            "interests": ["Cybersecurity"],
            "subjects": ["Computer Science"],
            "education": "B.Tech",
            "work_style": ["Technical", "Independent"],
            "experience": "Intermediate"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        careers_names = [r["career"] for r in results]
        self.assertIn("Cybersecurity Analyst", careers_names[:2])

    def test_tc05_different_education_qualification(self):
        """TC-05: Non-engineering degree (Other/Diploma) respects eligible education."""
        profile = {
            "skills": ["UI Design", "Figma", "Creativity", "Communication"],
            "interests": ["Design"],
            "subjects": ["English"],
            "education": "Other",
            "work_style": ["Creative", "Collaborative"],
            "experience": "Beginner"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        top_career = results[0]
        self.assertEqual(top_career["career"], "UI/UX Designer")
        self.assertTrue(top_career["education_matched"])

    def test_tc06_different_work_styles_management(self):
        """TC-06: Leadership and Collaborative work style properly activates Product Manager / Business Analyst."""
        profile = {
            "skills": ["Leadership", "Communication", "Problem Solving", "Data Analysis"],
            "interests": ["Management", "Business"],
            "subjects": ["Business Studies", "Economics"],
            "education": "B.Tech",
            "work_style": ["Leadership", "Collaborative"],
            "experience": "Intermediate"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        top_careers = [r["career"] for r in results[:2]]
        self.assertTrue("Product Manager" in top_careers or "Business Analyst" in top_careers)

    def test_tc07_beginner_user_profile(self):
        """TC-07: Beginner profile matches beginner-accepting careers."""
        profile = {
            "skills": ["Java", "DSA", "Problem Solving"],
            "interests": ["Programming"],
            "subjects": ["Computer Science", "Mathematics"],
            "education": "B.Tech",
            "work_style": ["Technical"],
            "experience": "Beginner"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        self.assertGreater(len(results), 0)
        self.assertTrue(results[0]["experience_matched"])

    def test_tc08_advanced_user_profile(self):
        """TC-08: Advanced profile matches specialized senior roles."""
        profile = {
            "skills": ["Solidity", "Blockchain", "C++", "Git"],
            "interests": ["Blockchain", "Technology"],
            "subjects": ["Computer Science", "Mathematics"],
            "education": "M.Tech",
            "work_style": ["Technical", "Independent"],
            "experience": "Advanced"
        }
        results = recommend_careers(self.careers, profile, top_n=5)
        self.assertEqual(results[0]["career"], "Blockchain Developer")
        self.assertEqual(results[0]["score"], 11)

    def test_tc09_deterministic_reproducibility(self):
        """TC-09: Identical user profile inputs must produce identical outputs and scores."""
        profile = {
            "skills": ["Python", "Git", "Linux", "Cloud", "Docker"],
            "interests": ["Cloud Computing", "Technology"],
            "subjects": ["Computer Science"],
            "education": "B.Tech",
            "work_style": ["Technical"],
            "experience": "Intermediate"
        }
        run_1 = recommend_careers(self.careers, profile, top_n=5)
        run_2 = recommend_careers(self.careers, profile, top_n=5)

        self.assertEqual([r["career"] for r in run_1], [r["career"] for r in run_2])
        self.assertEqual([r["score"] for r in run_1], [r["score"] for r in run_2])
        self.assertEqual([r["match_percentage"] for r in run_1], [r["match_percentage"] for r in run_2])

    def test_tc10_different_profiles_produce_different_rankings(self):
        """TC-10: Divergent profiles must produce distinct top recommendations."""
        profile_designer = {
            "skills": ["UI Design", "Figma", "Creativity"],
            "interests": ["Design"],
            "subjects": ["English"],
            "education": "BCA",
            "work_style": ["Creative"],
            "experience": "Beginner"
        }
        profile_coder = {
            "skills": ["C++", "Creativity", "Problem Solving"],
            "interests": ["Gaming", "Programming"],
            "subjects": ["Physics", "Mathematics"],
            "education": "B.Tech",
            "work_style": ["Creative", "Technical"],
            "experience": "Beginner"
        }
        res_designer = recommend_careers(self.careers, profile_designer, top_n=3)
        res_coder = recommend_careers(self.careers, profile_coder, top_n=3)

        self.assertNotEqual(res_designer[0]["career"], res_coder[0]["career"])
        self.assertEqual(res_designer[0]["career"], "UI/UX Designer")
        self.assertEqual(res_coder[0]["career"], "Game Developer")

if __name__ == "__main__":
    unittest.main()
