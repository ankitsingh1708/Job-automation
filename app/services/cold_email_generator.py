from typing import Dict, Any, Optional

def generate_cold_outreach_email(
    post: Dict[str, Any],
    resume_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Generates a personalized cold email to the hiring manager / recruiter referencing their post.
    """
    author_name = post.get("author_name", "Hiring Team").split()[0]
    author_company = post.get("author_company", "your team")
    post_role = post.get("skills", ["Software Engineering"])[0] if post.get("skills") else "Software Engineer"
    
    candidate_name = resume_profile.get("candidate_name", "Ankur Singh") if resume_profile else "Ankur Singh"
    candidate_title = resume_profile.get("candidate_title", "Software Engineer") if resume_profile else "Software Engineer"
    exp_years = resume_profile.get("experience_years", 4) if resume_profile else 4
    skills = resume_profile.get("skills", ["Python", "FastAPI", "React", "AWS"]) if resume_profile else ["Python", "FastAPI", "React", "AWS"]
    skills_str = ", ".join(skills[:4])
    
    subject = f"Application: {candidate_title} (via your LinkedIn update) - {candidate_name}"
    
    body = f"""Hi {author_name},

I came across your recent update on LinkedIn regarding engineering openings at {author_company} and was immediately drawn to what you are building.

I am a {candidate_title} with {exp_years}+ years of experience building scalable backend systems, microservices, and distributed cloud applications. My core stack includes {skills_str}.

A quick snapshot of what I bring to the table:
• Designed and shipped high-throughput APIs and distributed services.
• Strong hands-on proficiency in {skills_str} and relational/NoSQL datastores.
• Comfortable working in fast-paced product environments with high ownership.

I would love to explore how my background aligns with your current technical goals at {author_company}. 

I have attached my resume for your review. You can also view my GitHub at https://github.com/ankitsingh1708.

Looking forward to hearing from you!

Best regards,
{candidate_name}
Bengaluru, India
+91 9876543210
"""

    return {
        "subject": subject,
        "recipient_email": post.get("extracted_emails", ["recruiter@company.com"])[0] if post.get("extracted_emails") else "recruiter@company.com",
        "body": body
    }
