"""
Database seeding script to initialize sample recruiter, sample jobs, and sample resumes with AI match scores.
"""
import os
import json
import shutil
from backend import create_app
from backend.database import db
from backend.models import User, Job, Resume, MatchResult
from backend.services.resume_parser import ResumeParser
from backend.services.scoring import CandidateScorer
from config import Config

def seed():
    app = create_app(Config)
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # 1. Create Recruiter User if not exists
        recruiter = User.query.filter_by(email="recruiter@example.com").first()
        if not recruiter:
            print("Creating sample recruiter: recruiter@example.com / password123")
            recruiter = User(
                name="Sarah Jenkins",
                email="recruiter@example.com",
                role="recruiter"
            )
            recruiter.set_password("password123")
            db.session.add(recruiter)
            db.session.commit()

        # 2. Create Sample Jobs
        sample_jobs_data = [
            {
                "title": "Senior Python Backend Developer",
                "description": "Looking for an experienced Python developer to build scalable backend microservices, REST APIs, and database schemas with Flask, SQLAlchemy, PostgreSQL, and Docker. Experience with automated testing and CI/CD pipelines is strongly desired.",
                "required_skills": ["Python", "Flask", "SQL", "REST API", "Git"],
                "preferred_skills": ["Docker", "AWS", "PostgreSQL", "pytest"],
                "experience": "2-4 years",
                "education": "B.Tech in Computer Science / IT or equivalent"
            },
            {
                "title": "Full-Stack Web Developer",
                "description": "We are seeking a versatile Full-Stack Web Developer proficient in building dynamic web applications. Must have hands-on experience with Python backend frameworks and modern frontend JavaScript / React technologies.",
                "required_skills": ["Python", "JavaScript", "React", "SQL", "HTML", "CSS"],
                "preferred_skills": ["Node.js", "Docker", "REST API"],
                "experience": "1-3 years",
                "education": "Bachelor's Degree in Software Engineering"
            }
        ]

        jobs = []
        for j_data in sample_jobs_data:
            existing = Job.query.filter_by(title=j_data["title"]).first()
            if not existing:
                print(f"Creating sample job: {j_data['title']}")
                job = Job(
                    title=j_data["title"],
                    description=j_data["description"],
                    required_skills=json.dumps(j_data["required_skills"]),
                    preferred_skills=json.dumps(j_data["preferred_skills"]),
                    experience=j_data["experience"],
                    education=j_data["education"],
                    created_by=recruiter.id
                )
                db.session.add(job)
                jobs.append(job)
            else:
                jobs.append(existing)
        db.session.commit()

        # 3. Seed Sample Resumes
        sample_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample_resumes")
        upload_dir = app.config.get("UPLOAD_FOLDER")
        os.makedirs(upload_dir, exist_ok=True)

        sample_files = [
            ("alice_backend_developer.txt", "Alice Walker", "alice.walker@email.com", "+1-555-019-2834"),
            ("bob_frontend_developer.txt", "Bob Martinez", "bob.martinez@email.com", "+1-555-014-9922"),
            ("carol_ml_engineer.docx", "Carol Danvers", "carol.danvers@email.com", "+1-555-832-1102"),
            ("david_fullstack_developer.pdf", "David Kumar", "david.kumar@techmail.com", "+1-555-481-9032")
        ]

        resumes = []
        for filename, name, email, phone in sample_files:
            src_path = os.path.join(sample_dir, filename)
            if not os.path.exists(src_path):
                continue

            existing_resume = Resume.query.filter_by(filename=filename).first()
            if not existing_resume:
                dest_path = os.path.join(upload_dir, filename)
                shutil.copyfile(src_path, dest_path)

                extracted_text = ResumeParser.extract_text_from_file(dest_path)
                resume = Resume(
                    candidate_name=name,
                    candidate_email=email,
                    candidate_phone=phone,
                    filename=filename,
                    file_path=dest_path,
                    extracted_text=extracted_text
                )
                db.session.add(resume)
                resumes.append(resume)
                print(f"Added resume: {name} ({filename})")
            else:
                resumes.append(existing_resume)
        db.session.commit()

        # 4. Run Matching Pipeline for Seed Data
        scorer = CandidateScorer(
            weight_tfidf=app.config.get("WEIGHT_TFIDF", 0.30),
            weight_semantic=app.config.get("WEIGHT_SEMANTIC", 0.40),
            weight_skill=app.config.get("WEIGHT_SKILL", 0.30)
        )

        for job in jobs:
            for resume in resumes:
                match = MatchResult.query.filter_by(job_id=job.id, resume_id=resume.id).first()
                if not match:
                    eval_result = scorer.evaluate_candidate(
                        job_description=job.description,
                        required_skills=job.get_required_skills_list(),
                        resume_text=resume.extracted_text,
                        preferred_skills=job.get_preferred_skills_list()
                    )
                    match = MatchResult(
                        job_id=job.id,
                        resume_id=resume.id,
                        tfidf_score=eval_result["tfidf_score"],
                        semantic_score=eval_result["semantic_score"],
                        skill_score=eval_result["skill_score"],
                        overall_score=eval_result["overall_score"],
                        matched_skills=json.dumps(eval_result["matched_skills"]),
                        missing_skills=json.dumps(eval_result["missing_skills"]),
                        strong_areas=json.dumps(eval_result["strong_areas"]),
                        weak_areas=json.dumps(eval_result["weak_areas"])
                    )
                    db.session.add(match)
        db.session.commit()
        print("\nDatabase seeded successfully!")
        print("Recruiter login credentials: recruiter@example.com / password123")

if __name__ == "__main__":
    seed()
