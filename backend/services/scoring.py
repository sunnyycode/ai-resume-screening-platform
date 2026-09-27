from backend.services.tfidf_matcher import TFIDFMatcher
from backend.services.semantic_matcher import SemanticMatcher
from backend.services.skill_matcher import match_skills

class CandidateScorer:
    """
    Coordinates multi-faceted resume-to-job matching:
    1. Keyword Relevance (TF-IDF)
    2. Contextual Understanding (Semantic Sentence Transformers)
    3. Exact Skill Coverage (Skill Taxonomy)
    
    Produces an overall percentage score and an explainable breakdown of strengths and gaps.
    """

    def __init__(self, weight_tfidf: float = 0.30, weight_semantic: float = 0.40, weight_skill: float = 0.30):
        # Normalize weights so they always sum to 1.0
        total_weight = weight_tfidf + weight_semantic + weight_skill
        if total_weight <= 0:
            self.w_tfidf = 0.30
            self.w_semantic = 0.40
            self.w_skill = 0.30
        else:
            self.w_tfidf = weight_tfidf / total_weight
            self.w_semantic = weight_semantic / total_weight
            self.w_skill = weight_skill / total_weight

        self.tfidf_matcher = TFIDFMatcher()
        self.semantic_matcher = SemanticMatcher()

    def evaluate_candidate(
        self,
        job_description: str,
        required_skills: list[str],
        resume_text: str,
        preferred_skills: list[str] = None
    ) -> dict:
        """
        Calculates all sub-scores, combines them according to configured weights,
        and constructs an explainable evaluation report.
        """
        # Full job context combining description and required skills
        skills_str = ", ".join(required_skills) if required_skills else ""
        full_job_context = f"{job_description}\nKey Requirements: {skills_str}"

        # 1. TF-IDF Keyword Match
        tfidf_score = self.tfidf_matcher.compute_similarity(full_job_context, resume_text)

        # 2. Semantic Contextual Match
        semantic_score = self.semantic_matcher.compute_similarity(full_job_context, resume_text)

        # 3. Exact Skill Extraction and Matching
        skill_analysis = match_skills(required_skills, resume_text, preferred_skills)
        skill_score = skill_analysis["skill_score"]

        # 4. Weighted Combined Score (0.0 to 1.0 scale)
        raw_final_score = (
            (self.w_tfidf * tfidf_score) +
            (self.w_semantic * semantic_score) +
            (self.w_skill * skill_score)
        )

        overall_percentage = round(raw_final_score * 100, 2)
        tfidf_percentage = round(tfidf_score * 100, 2)
        semantic_percentage = round(semantic_score * 100, 2)
        skill_percentage = round(skill_score * 100, 2)

        # Determine qualitative fit recommendation
        if overall_percentage >= 80:
            recommendation = "Strong Match - Recommended for Interview"
            fit_tier = "High"
        elif overall_percentage >= 60:
            recommendation = "Moderate Match - Potential Candidate"
            fit_tier = "Medium"
        else:
            recommendation = "Low Match - Does not meet key requirements"
            fit_tier = "Low"

        # Point contribution breakdown for transparency
        contributions = {
            "tfidf_points": round(self.w_tfidf * tfidf_percentage, 2),
            "semantic_points": round(self.w_semantic * semantic_percentage, 2),
            "skill_points": round(self.w_skill * skill_percentage, 2)
        }

        return {
            "overall_score": overall_percentage,
            "tfidf_score": tfidf_score,
            "tfidf_percentage": tfidf_percentage,
            "semantic_score": semantic_score,
            "semantic_percentage": semantic_percentage,
            "skill_score": skill_score,
            "skill_percentage": skill_percentage,
            "weights": {
                "tfidf": round(self.w_tfidf, 2),
                "semantic": round(self.w_semantic, 2),
                "skill": round(self.w_skill, 2)
            },
            "contributions": contributions,
            "matched_skills": skill_analysis["matched_skills"],
            "missing_skills": skill_analysis["missing_skills"],
            "matched_preferred": skill_analysis["matched_preferred"],
            "all_resume_skills": skill_analysis["all_resume_skills"],
            "strong_areas": skill_analysis["strong_areas"],
            "weak_areas": skill_analysis["weak_areas"],
            "recommendation": recommendation,
            "fit_tier": fit_tier
        }
