import re

# Comprehensive catalog of technical skills
SKILL_CATALOG = {
    # Programming Languages
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "go", "golang", 
    "rust", "ruby", "php", "swift", "kotlin", "scala", "dart", "r", "shell", "bash",
    
    # Web & Frameworks
    "html", "css", "html5", "css3", "react", "react.js", "next.js", "vue", "vue.js", 
    "angular", "svelte", "node.js", "express", "express.js", "flask", "django", 
    "fastapi", "spring", "spring boot", "asp.net", "laravel", "rails", "tailwind css", "bootstrap",
    
    # Databases & Caching
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "elasticsearch", 
    "cassandra", "oracle", "mariadb", "dynamodb", "neo4j", "firebase",
    
    # Cloud & DevOps
    "docker", "kubernetes", "k8s", "aws", "amazon web services", "azure", "gcp", 
    "google cloud", "ci/cd", "jenkins", "github actions", "gitlab ci", "terraform", 
    "ansible", "nginx", "linux", "git", "github", "bitbucket",
    
    # AI / ML & Data Science
    "machine learning", "deep learning", "nlp", "natural language processing", 
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", 
    "pandas", "numpy", "matplotlib", "seaborn", "opencv", "scipy", "huggingface", 
    "transformers", "large language models", "llm", "data analysis", "bigquery",
    
    # Architecture, APIs & Concepts
    "rest api", "restful api", "graphql", "microservices", "system design", 
    "object oriented programming", "oop", "data structures", "algorithms", 
    "agile", "scrum", "unit testing", "pytest", "jest", "web sockets"
}

# Aliases and canonical normalization
SKILL_ALIASES = {
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "vue.js": "Vue.js",
    "vue": "Vue.js",
    "angular.js": "Angular",
    "angular": "Angular",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "express.js": "Express",
    "express": "Express",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "html5": "HTML5",
    "html": "HTML",
    "css3": "CSS3",
    "css": "CSS",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "ci/cd": "CI/CD",
    "git": "Git",
    "github": "GitHub",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "spring boot": "Spring Boot",
    "spring": "Spring Boot",
    "rest api": "REST API",
    "restful api": "REST API",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "pytest": "pytest",
    "microservices": "Microservices",
    "graphql": "GraphQL",
    "linux": "Linux"
}

# Domain mapping for strong/weak area explanations
DOMAIN_CLUSTERS = {
    "Backend Development": {"Python", "Java", "C++", "C#", "Go", "Flask", "Django", "FastAPI", "Spring Boot", "REST API", "Microservices"},
    "Frontend Development": {"JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Next.js", "HTML", "CSS", "Tailwind CSS"},
    "Databases & Storage": {"SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis"},
    "Cloud & DevOps": {"Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Git", "GitHub", "Linux"},
    "AI / Machine Learning": {"Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy"}
}

def canonicalize_skill(skill: str) -> str:
    """Normalize skill string to its standard display format."""
    clean = skill.strip().lower()
    return SKILL_ALIASES.get(clean, skill.strip().title())

def extract_skills_from_text(text: str) -> list[str]:
    """
    Extract technical skills from text using boundary matching.
    Handles special characters like C++, C#, .NET, CI/CD, Node.js properly.
    """
    if not text:
        return []

    found_skills = set()
    lowered = f" {text.lower()} "

    # Check for symbols first
    if re.search(r"(?:\b|\s)c\+\+(?:\b|\s|[,\.;])", lowered):
        found_skills.add("C++")
    if re.search(r"(?:\b|\s)c\#(?:\b|\s|[,\.;])", lowered):
        found_skills.add("C#")
    if re.search(r"(?:\b|\s)\.net(?:\b|\s|[,\.;])", lowered):
        found_skills.add(".NET")
    if re.search(r"(?:\b|\s)ci/cd(?:\b|\s|[,\.;])", lowered):
        found_skills.add("CI/CD")
    if re.search(r"(?:\b|\s)node(?:\.js)?(?:\b|\s|[,\.;])", lowered):
        found_skills.add("Node.js")
    if re.search(r"(?:\b|\s)react(?:\.js)?(?:\b|\s|[,\.;])", lowered):
        found_skills.add("React")
    if re.search(r"(?:\b|\s)vue(?:\.js)?(?:\b|\s|[,\.;])", lowered):
        found_skills.add("Vue.js")
    if re.search(r"(?:\b|\s)next(?:\.js)?(?:\b|\s|[,\.;])", lowered):
        found_skills.add("Next.js")
    if re.search(r"(?:\b|\s)rest(?:ful)?\s+api[s]?(?:\b|\s|[,\.;])", lowered):
        found_skills.add("REST API")

    # Check words from catalog
    for skill in SKILL_CATALOG:
        # Skip special symbols handled above
        if skill in {"c++", "c#", ".net", "ci/cd", "node.js", "react.js", "vue.js", "next.js", "rest api", "restful api"}:
            continue

        pattern = rf"(?:\b|\s){re.escape(skill)}(?:\b|\s|[,\.;:\(\)])"
        if re.search(pattern, lowered):
            canonical = canonicalize_skill(skill)
            found_skills.add(canonical)

    return sorted(list(found_skills))

def match_skills(required_skills: list[str], resume_text: str, preferred_skills: list[str] = None) -> dict:
    """
    Match required skills and preferred skills against resume text.
    
    Returns:
    - matched_skills: list of required skills present in resume
    - missing_skills: list of required skills absent in resume
    - matched_preferred: list of preferred skills present in resume
    - skill_score: float ratio of (matched / total_required) in [0.0, 1.0]
    - strong_areas: domain areas where skills match strongly
    - weak_areas: domain areas where skills are missing
    """
    resume_skills = extract_skills_from_text(resume_text)
    resume_skills_lower = {s.lower() for s in resume_skills}

    # Normalize required skills
    normalized_required = []
    for r in (required_skills or []):
        if isinstance(r, str) and r.strip():
            # If comma-separated, split
            parts = [p.strip() for p in r.split(",") if p.strip()]
            for p in parts:
                normalized_required.append(canonicalize_skill(p))

    # Remove duplicates preserving order
    clean_required = []
    for r in normalized_required:
        if r not in clean_required:
            clean_required.append(r)

    matched_skills = []
    missing_skills = []

    for req in clean_required:
        req_clean = req.lower()
        # Direct check or substring match
        if req_clean in resume_skills_lower:
            matched_skills.append(req)
        elif any(alias_clean in resume_skills_lower for alias_raw, alias_clean in [
            ("javascript", "js"), ("typescript", "ts"), ("kubernetes", "k8s"), ("postgresql", "postgres")
        ] if req_clean == alias_raw or req_clean == alias_clean):
            matched_skills.append(req)
        else:
            # Check if skill literally appears in raw text with word boundaries
            pattern = rf"(?:\b|\s){re.escape(req_clean)}(?:\b|\s|[,\.;:\(\)])"
            if re.search(pattern, f" {resume_text.lower()} "):
                matched_skills.append(req)
            else:
                missing_skills.append(req)

    # Preferred skills matching
    matched_preferred = []
    if preferred_skills:
        for pref in preferred_skills:
            if isinstance(pref, str) and pref.strip():
                canon = canonicalize_skill(pref)
                if canon.lower() in resume_skills_lower:
                    matched_preferred.append(canon)

    total_required = len(clean_required)
    if total_required == 0:
        base_skill_score = 1.0
    else:
        # Base ratio of matched required skills
        base_ratio = len(matched_skills) / total_required
        # Slight bonus for preferred skills (up to 0.10 max)
        bonus = min(0.10, len(matched_preferred) * 0.05) if preferred_skills else 0.0
        base_skill_score = min(1.0, base_ratio + bonus)

    # Classify domain strong and weak areas
    strong_areas = []
    weak_areas = []

    matched_set = set(matched_skills)
    missing_set = set(missing_skills)

    for domain, domain_skills in DOMAIN_CLUSTERS.items():
        domain_matched = domain_skills.intersection(matched_set)
        domain_missing = domain_skills.intersection(missing_set)

        if domain_matched:
            strong_areas.append(f"{domain} ({', '.join(sorted(list(domain_matched)))})")
        if domain_missing:
            weak_areas.append(f"{domain} missing ({', '.join(sorted(list(domain_missing)))})")

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_preferred": matched_preferred,
        "all_resume_skills": resume_skills,
        "skill_score": round(base_skill_score, 4),
        "strong_areas": strong_areas,
        "weak_areas": weak_areas
    }
