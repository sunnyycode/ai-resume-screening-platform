from backend.services.text_preprocessor import clean_text
from backend.services.tfidf_matcher import TFIDFMatcher
from backend.services.skill_matcher import extract_skills_from_text, match_skills
from backend.services.semantic_matcher import SemanticMatcher
from backend.services.scoring import CandidateScorer

def test_text_preprocessor_preserves_tech_terms():
    raw = "Experienced in C++, C#, .NET, Node.js, and REST API development!"
    cleaned = clean_text(raw)
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert ".net" in cleaned
    assert "node.js" in cleaned
    assert "rest api" in cleaned

def test_skill_extraction():
    text = "Proficient in Python, SQL, Docker, React.js, and AWS."
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "React" in skills
    assert "AWS" in skills

def test_skill_matching_exact_and_missing():
    required = ["Python", "Flask", "SQL", "Docker", "AWS"]
    resume = "Experienced Python developer with Flask and SQL skills. Uses Git."
    result = match_skills(required, resume)

    assert "Python" in result["matched_skills"]
    assert "Flask" in result["matched_skills"]
    assert "SQL" in result["matched_skills"]
    assert "Docker" in result["missing_skills"]
    assert "AWS" in result["missing_skills"]
    assert 0.5 <= result["skill_score"] <= 0.7  # 3 out of 5 matched = 0.6

def test_tfidf_matcher_bounds_and_relevance():
    matcher = TFIDFMatcher()
    job = "Senior Python engineer building Flask web applications and SQL databases."
    matching_resume = "Skilled Python developer with extensive Flask and SQL database experience."
    unrelated_resume = "Graphic designer specializing in Adobe Photoshop and marketing brochures."

    sim_high = matcher.compute_similarity(job, matching_resume)
    sim_low = matcher.compute_similarity(job, unrelated_resume)

    assert 0.0 <= sim_high <= 1.0
    assert 0.0 <= sim_low <= 1.0
    assert sim_high > sim_low

def test_semantic_matcher_conceptual_similarity():
    matcher = SemanticMatcher()
    job = "Experience with machine learning, neural networks, and predictive analytics."
    resume = "Built deep learning models, classification algorithms, and artificial intelligence solutions."
    
    sim = matcher.compute_similarity(job, resume)
    assert 0.0 <= sim <= 1.0
    assert sim > 0.05  # Shows semantic awareness beyond exact string match

def test_candidate_scorer_weighted_formula():
    scorer = CandidateScorer(weight_tfidf=0.30, weight_semantic=0.40, weight_skill=0.30)
    job_desc = "Looking for a Python Flask developer with SQL expertise."
    req_skills = ["Python", "Flask", "SQL"]
    resume_text = "Senior Python developer with 4 years in Flask, PostgreSQL, and SQL."

    eval_result = scorer.evaluate_candidate(
        job_description=job_desc,
        required_skills=req_skills,
        resume_text=resume_text
    )

    assert "overall_score" in eval_result
    assert 0 <= eval_result["overall_score"] <= 100
    assert eval_result["tfidf_score"] >= 0
    assert eval_result["semantic_score"] >= 0
    assert eval_result["skill_score"] == 1.0  # Python, Flask, SQL all present
    assert "matched_skills" in eval_result
    assert "missing_skills" in eval_result
    assert "contributions" in eval_result
