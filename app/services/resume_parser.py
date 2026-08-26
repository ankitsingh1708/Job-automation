import re
import io
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

COMMON_SKILLS = [
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css",
    # Frameworks & Libraries
    "react", "react.js", "next.js", "vue", "vue.js", "angular", "node.js", "express", "fastapi", "django", "flask", "spring boot", "asp.net", "laravel", "graphql", "rest api", "tailwind", "bootstrap",
    # AI / ML / Data
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "keras", "opencv", "llm", "large language models", "transformers", "huggingface", "langchain", "rag", "fine-tuning", "machine learning", "deep learning", "nlp", "computer vision", "generative ai", "spark", "hadoop", "databricks", "airflow",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ansible", "ci/cd", "github actions", "gitlab ci", "jenkins", "helm", "prometheus", "grafana", "linux", "bash",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "cassandra", "dynamodb", "snowflake", "bigquery",
    # Tools & Methods
    "git", "github", "gitlab", "jira", "agile", "scrum", "microservices", "distributed systems", "system design", "unit testing", "cybersecurity", "owasp"
]

TITLES_LIST = [
    "software engineer", "full stack developer", "full stack engineer", "frontend engineer", "frontend developer",
    "backend engineer", "backend developer", "ai engineer", "machine learning engineer", "data scientist",
    "data engineer", "devops engineer", "cloud architect", "product manager", "engineering manager",
    "security engineer", "qa engineer", "mobile developer", "ios developer", "android developer"
]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        return ""

def parse_resume_text(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    # Extract Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None

    # Extract Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else None

    # Extract Skills
    found_skills = []
    for skill in COMMON_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill.title())
    
    # Deduplicate & preserve standard casing
    found_skills = list(dict.fromkeys(found_skills))

    # Extract likely Role / Title
    detected_title = "Software Engineer"
    for title in TITLES_LIST:
        if title in text_lower:
            detected_title = title.title()
            break

    # Estimate Experience Years
    exp_years = 3
    exp_matches = re.findall(r'(\d+)\+?\s*(?:years|yrs)\s+(?:of\s+)?(?:experience|exp)', text_lower)
    if exp_matches:
        try:
            exp_years = max([int(m) for m in exp_matches if int(m) < 40])
        except Exception:
            exp_years = 3

    # Generate Recommended Search Queries
    search_queries = [detected_title]
    if "Python" in found_skills:
        search_queries.append("Python Developer")
    if "React" in found_skills or "Next.Js" in found_skills:
        search_queries.append("Frontend React Engineer")
    if "Pytorch" in found_skills or "Machine Learning" in found_skills or "Llm" in found_skills:
        search_queries.append("AI / Machine Learning Engineer")
    if "Aws" in found_skills or "Docker" in found_skills:
        search_queries.append("Cloud / DevOps Engineer")

    return {
        "candidate_title": detected_title,
        "email": email,
        "phone": phone,
        "experience_years": exp_years,
        "skills": found_skills,
        "raw_length": len(text),
        "search_queries": list(dict.fromkeys(search_queries))[:4]
    }

def calculate_job_match(resume_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    candidate_skills = set(s.lower() for s in resume_profile.get("skills", []))
    
    # Combine job search fields
    job_title = job.get("title", "").lower()
    job_desc = (job.get("description", "") + " " + job.get("description_text", "")).lower()
    job_skills = set(s.lower() for s in job.get("skills", []))

    # Check which candidate skills appear in job description/skills
    matched_skills = []
    for skill in candidate_skills:
        if skill in job_desc or skill in job_title or skill in job_skills:
            matched_skills.append(skill.title())

    # Detect missing required skills from job
    missing_skills = []
    for common_skill in COMMON_SKILLS:
        if common_skill in job_desc and common_skill not in candidate_skills:
            missing_skills.append(common_skill.title())

    # Score calculation
    # Base score: Skill overlap percentage (0-60)
    skill_score = min(60, len(matched_skills) * 8)
    
    # Title synergy score (0-25)
    title_score = 0
    candidate_title = resume_profile.get("candidate_title", "").lower()
    if candidate_title and any(word in job_title for word in candidate_title.split() if len(word) > 3):
        title_score = 25
    elif any(s.lower() in job_title for s in candidate_skills):
        title_score = 15
    else:
        title_score = 10

    # Experience synergy (0-15)
    exp_score = 15

    total_score = min(98, skill_score + title_score + exp_score)
    # Give reasonable floor for relevant searches
    if matched_skills:
        total_score = max(55, total_score)
    else:
        total_score = max(35, total_score)

    if total_score >= 85:
        verdict = "Strong Match"
        color = "emerald"
    elif total_score >= 70:
        verdict = "Good Fit"
        color = "blue"
    elif total_score >= 50:
        verdict = "Partial Fit"
        color = "amber"
    else:
        verdict = "Stretch Opportunity"
        color = "slate"

    return {
        "job_id": job.get("id"),
        "match_score": total_score,
        "verdict": verdict,
        "badge_color": color,
        "matched_skills": matched_skills[:8],
        "missing_skills": missing_skills[:5]
    }

def generate_custom_cover_letter(resume_profile: Dict[str, Any], job: Dict[str, Any]) -> str:
    candidate_title = resume_profile.get("candidate_title", "Software Engineer")
    years_exp = resume_profile.get("experience_years", 3)
    skills = resume_profile.get("skills", ["Python", "FastAPI", "Cloud Infrastructure"])
    top_skills = ", ".join(skills[:4]) if skills else "modern software engineering practices"

    job_title = job.get("title", "the open position")
    company = job.get("company_name", "your team")
    location = job.get("location", "the listed location")

    letter = f"""Dear Hiring Team at {company},

I am writing to express my strong enthusiasm for the {job_title} role based in {location}. With over {years_exp}+ years of hands-on experience as a {candidate_title}, coupled with deep expertise in {top_skills}, I am confident in my ability to deliver immediate technical impact to your engineering organization.

Throughout my career, I have focused on architecting resilient, high-throughput systems, writing maintainable code, and partnering with product teams to translate complex requirements into reliable end-user products. The work that {company} is doing aligns closely with my technical background and passion for building scalable solutions.

Key highlights I bring to {company}:
• Proven proficiency across {top_skills}, enabling rapid onboarding and architectural velocity.
• Experience leading technical initiatives from conception through CI/CD deployment and production monitoring.
• A collaborative mindset dedicated to agile execution, code quality, and cross-functional teamwork.

I welcome the opportunity to discuss how my qualifications, technical skills, and drive can contribute to the ongoing success of {company}. Thank you for your time and consideration.

Sincerely,
Candidate
"""
    return letter.strip()
