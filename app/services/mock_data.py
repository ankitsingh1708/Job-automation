import random
from typing import List, Dict, Any

COMPANIES = [
    {"name": "Google", "logo": "https://logo.clearbit.com/google.com", "rating": 4.5, "size": "100,000+ employees"},
    {"name": "Microsoft", "logo": "https://logo.clearbit.com/microsoft.com", "rating": 4.4, "size": "100,000+ employees"},
    {"name": "Amazon", "logo": "https://logo.clearbit.com/amazon.com", "rating": 4.1, "size": "100,000+ employees"},
    {"name": "Stripe", "logo": "https://logo.clearbit.com/stripe.com", "rating": 4.6, "size": "5,000-10,000 employees"},
    {"name": "OpenAI", "logo": "https://logo.clearbit.com/openai.com", "rating": 4.8, "size": "1,000-5,000 employees"},
    {"name": "Anthropic", "logo": "https://logo.clearbit.com/anthropic.com", "rating": 4.9, "size": "500-1,000 employees"},
    {"name": "Meta", "logo": "https://logo.clearbit.com/meta.com", "rating": 4.3, "size": "50,000+ employees"},
    {"name": "Apple", "logo": "https://logo.clearbit.com/apple.com", "rating": 4.4, "size": "100,000+ employees"},
    {"name": "Flipkart", "logo": "https://logo.clearbit.com/flipkart.com", "rating": 4.2, "size": "30,000+ employees"},
    {"name": "Databricks", "logo": "https://logo.clearbit.com/databricks.com", "rating": 4.7, "size": "5,000-10,000 employees"},
    {"name": "Uber", "logo": "https://logo.clearbit.com/uber.com", "rating": 4.2, "size": "20,000+ employees"},
    {"name": "Swiggy", "logo": "https://logo.clearbit.com/swiggy.com", "rating": 4.3, "size": "10,000+ employees"},
    {"name": "Zomato", "logo": "https://logo.clearbit.com/zomato.com", "rating": 4.2, "size": "5,000-10,000 employees"},
    {"name": "Razorpay", "logo": "https://logo.clearbit.com/razorpay.com", "rating": 4.5, "size": "3,000-5,000 employees"},
]

JOB_TEMPLATES = [
    {
        "title": "Senior Full Stack Engineer (Python / React)",
        "category": "Software Engineering",
        "job_type": "Full-time",
        "experience_level": "Mid-Senior level",
        "workplace_type": "Remote",
        "salary": "₹24L - ₹42L / yr",
        "description": "We are looking for a Senior Full Stack Engineer to lead architectural design and development of our modern core web applications and microservices. You will work across modern Python, FastAPI, React, TypeScript, and AWS cloud services.\n\nKey Responsibilities:\n- Architect, build, and maintain scalable APIs and responsive web interfaces.\n- Partner with product managers and designers to translate product vision into reliable features.\n- Optimize database queries, caching strategies, and asynchronous task workers.\n- Mentor junior engineers and participate in comprehensive code reviews.\n\nRequirements:\n- 5+ years of experience with modern backend (Python/Django/FastAPI or Node.js) and frontend (React/Vue/TypeScript).\n- Experience with relational and NoSQL databases (PostgreSQL, Redis).\n- Solid understanding of CI/CD, Docker, and cloud infrastructure (AWS/GCP).",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS"]
    },
    {
        "title": "AI / Machine Learning Research Engineer",
        "category": "AI / Machine Learning",
        "job_type": "Full-time",
        "experience_level": "Mid-Senior level",
        "workplace_type": "Hybrid",
        "salary": "₹28L - ₹52L / yr",
        "description": "Join our AI team to train, fine-tune, and deploy state-of-the-art Large Language Models and multimodal foundation models. You will be building cutting-edge inference engines and retrieval-augmented systems.\n\nKey Responsibilities:\n- Conduct research and experimental training on LLMs, agent frameworks, and multi-modal models.\n- Design efficient distributed training pipelines with PyTorch and Ray.\n- Deploy low-latency inference pipelines with vLLM, TensorRT-LLM, and Triton.\n- Collaborate with product teams to embed generative AI capabilities into end-user products.\n\nRequirements:\n- MS or PhD in Computer Science, Machine Learning, or equivalent practical experience.\n- Strong proficiency in PyTorch, Python, HuggingFace transformers, and CUDA optimization.\n- Experience fine-tuning foundation models and optimizing token throughput.",
        "skills": ["PyTorch", "Python", "LLMs", "Transformers", "CUDA", "LangChain", "vLLM"]
    },
    {
        "title": "Staff Backend Engineer - Distributed Systems",
        "category": "Software Engineering",
        "job_type": "Full-time",
        "experience_level": "Director / Staff",
        "workplace_type": "Remote",
        "salary": "₹45L - ₹75L / yr",
        "description": "We are seeking a Staff Backend Engineer to drive the next generation of our distributed event-driven infrastructure handling millions of transactions per second.\n\nKey Responsibilities:\n- Define technical roadmaps and system architecture for mission-critical services.\n- Solve complex distributed consensus, streaming, and scalability challenges.\n- Drive engineering excellence, high availability (99.999%), and disaster recovery readiness.\n\nRequirements:\n- 8+ years designing and scaling distributed systems with Go, Java, or Rust.\n- Deep understanding of Kafka, Cassandra, gRPC, and Kubernetes orchestration.\n- Proven track record of leading high-impact technical initiatives across engineering orgs.",
        "skills": ["Go", "Distributed Systems", "Kafka", "Kubernetes", "gRPC", "Microservices"]
    },
    {
        "title": "Frontend Engineer (React / Next.js / Tailwind)",
        "category": "Frontend Development",
        "job_type": "Full-time",
        "experience_level": "Entry level",
        "workplace_type": "Remote",
        "salary": "₹14L - ₹24L / yr",
        "description": "We are looking for a talented Frontend Engineer passionate about crafting seamless, pixel-perfect user experiences and lightning-fast web applications.\n\nKey Responsibilities:\n- Implement responsive UI components using React, Next.js, and Tailwind CSS.\n- Collaborate closely with UI/UX designers in Figma to create intuitive workflows.\n- Optimize Core Web Vitals, accessibility (a11y), and cross-browser performance.\n\nRequirements:\n- 2+ years of professional web development experience with React and modern JavaScript/TypeScript.\n- Strong understanding of CSS3, Tailwind, state management, and REST/GraphQL APIs.\n- Eye for detail and passion for delightful user interactions.",
        "skills": ["React", "Next.js", "Tailwind CSS", "TypeScript", "Figma", "Web Performance"]
    },
    {
        "title": "DevOps & Cloud Infrastructure Engineer",
        "category": "DevOps / Cloud",
        "job_type": "Full-time",
        "experience_level": "Mid-Senior level",
        "workplace_type": "Hybrid",
        "salary": "₹18L - ₹35L / yr",
        "description": "Seeking a DevOps Engineer to automate and scale our multi-region cloud infrastructure, improve developer velocity, and maintain airtight security standards.\n\nKey Responsibilities:\n- Manage Infrastructure as Code using Terraform and CloudFormation.\n- Maintain Kubernetes clusters, Prometheus/Grafana monitoring, and automated CI/CD pipelines.\n- Ensure zero-downtime deployments and enforce cloud security posture management.\n\nRequirements:\n- 4+ years in Cloud Engineering / DevOps role supporting production AWS or GCP environments.\n- Hands-on experience with Terraform, Kubernetes, Helm, and GitHub Actions.\n- Strong scripting skills in Python or Bash.",
        "skills": ["Terraform", "AWS", "Kubernetes", "CI/CD", "Docker", "Prometheus", "Python"]
    },
    {
        "title": "Lead Data Scientist - Predictive Modeling",
        "category": "Data Science",
        "job_type": "Full-time",
        "experience_level": "Mid-Senior level",
        "workplace_type": "On-site",
        "salary": "₹25L - ₹45L / yr",
        "description": "We are seeking a Lead Data Scientist to build predictive models, recommendation algorithms, and statistical experiment frameworks driving core growth metrics.\n\nKey Responsibilities:\n- Develop and operationalize machine learning models for forecasting, churn prediction, and user segmentation.\n- Design and analyze A/B tests to measure feature impact accurately.\n- Work with data engineering to build automated feature stores and ETL pipelines.\n\nRequirements:\n- 5+ years of industry experience applying ML and statistical models.\n- Expert in Python (Pandas, Scikit-learn, XGBoost) and advanced SQL.\n- Strong communication skills to present quantitative insights to stakeholders.",
        "skills": ["Python", "SQL", "Machine Learning", "A/B Testing", "Scikit-Learn", "Data Modeling"]
    },
    {
        "title": "Cybersecurity & AppSec Specialist",
        "category": "Security",
        "job_type": "Contract",
        "experience_level": "Mid-Senior level",
        "workplace_type": "Remote",
        "salary": "₹18L - ₹36L / yr",
        "description": "Protect our high-growth platform against evolving threats. You will conduct threat modeling, penetration testing, and integrate automated security scanners into our CI/CD pipeline.\n\nKey Responsibilities:\n- Perform vulnerability assessments and source code audits.\n- Partner with engineering teams to remediate OWASP Top 10 vulnerabilities.\n- Respond to security incidents and conduct root cause analysis.\n\nRequirements:\n- 4+ years of application security or penetration testing experience.\n- Certifications such as OSCP, CISSP, or CEH are highly regarded.\n- In-depth understanding of cloud security, cryptography, and network defense.",
        "skills": ["Application Security", "Penetration Testing", "OWASP", "Cloud Security", "Python"]
    },
    {
        "title": "Software Engineer Intern (Summer 2026)",
        "category": "Software Engineering",
        "job_type": "Internship",
        "experience_level": "Internship",
        "workplace_type": "Remote",
        "salary": "₹6L - ₹10L / yr",
        "description": "Join our summer internship program and work on real production software alongside experienced engineering mentors.\n\nKey Responsibilities:\n- Design and implement new features for our flagship web platforms.\n- Write clean, unit-tested code in Python, Go, or TypeScript.\n- Participate in agile standups, sprint planning, and hackathons.\n\nRequirements:\n- Currently pursuing a Bachelor's or Master's in Computer Science or related STEM field.\n- Solid foundation in data structures, algorithms, and object-oriented programming.",
        "skills": ["Python", "JavaScript", "Data Structures", "Git", "Algorithms"]
    },
    {
        "title": "Product Manager - Developer Platform",
        "category": "Product Management",
        "job_type": "Full-time",
        "experience_level": "Mid-Senior level",
        "workplace_type": "Hybrid",
        "salary": "₹24L - ₹48L / yr",
        "description": "Lead product strategy for our public APIs, developer SDKs, and integrations ecosystem used by over 50,000 developers worldwide.\n\nKey Responsibilities:\n- Define the product vision, roadmap, and success metrics for our developer tools.\n- Conduct user interviews, feedback loops, and competitive benchmarking.\n- Work closely with engineering and developer relations teams to launch features.\n\nRequirements:\n- 4+ years of product management experience with developer-focused or B2B SaaS products.\n- Technical background or ability to engage deeply with technical concepts.\n- Strong analytical and product storytelling skills.",
        "skills": ["Product Management", "API Design", "Agile", "User Research", "Roadmapping"]
    }
]

LOCATIONS = [
    "Bengaluru, Karnataka, India", "Hyderabad, Telangana, India", "Pune, Maharashtra, India",
    "Delhi NCR, India", "Mumbai, Maharashtra, India", "Chennai, Tamil Nadu, India",
    "Remote, India", "Noida, Uttar Pradesh, India", "Gurgaon, Haryana, India"
]

POSTED_TIMES = [
    "10 minutes ago", "2 hours ago", "5 hours ago", "1 day ago",
    "2 days ago", "3 days ago", "5 days ago", "1 week ago"
]

def generate_mock_jobs(keywords: str = "", location: str = "", limit: int = 25) -> List[Dict[str, Any]]:
    jobs = []
    kw_lower = keywords.lower().strip() if keywords else ""
    loc_lower = location.lower().strip() if location else ""

    all_combinations = []
    for comp in COMPANIES:
        for template in JOB_TEMPLATES:
            for loc in LOCATIONS:
                all_combinations.append((comp, template, loc))

    random.seed(42)
    random.shuffle(all_combinations)

    count = 1000
    for comp, template, loc in all_combinations:
        job_title = template["title"]
        desc = template["description"]
        skills_str = " ".join(template["skills"])
        
        if kw_lower:
            searchable_text = f"{job_title} {comp['name']} {template['category']} {skills_str} {desc}".lower()
            if not any(word in searchable_text for word in kw_lower.split()):
                continue

        if loc_lower:
            if loc_lower not in loc.lower() and (loc_lower != "remote" or template["workplace_type"] != "Remote"):
                continue

        job_id = f"mock-job-{count}"
        count += 1
        time_posted = random.choice(POSTED_TIMES)
        is_urgent = random.choice([True, False, False, False])
        is_easy_apply = random.choice([True, True, False])

        jobs.append({
            "id": job_id,
            "title": job_title,
            "company_name": comp["name"],
            "company_logo": comp["logo"],
            "company_rating": comp["rating"],
            "company_size": comp["size"],
            "location": loc,
            "workplace_type": template["workplace_type"],
            "job_type": template["job_type"],
            "experience_level": template["experience_level"],
            "salary": template["salary"],
            "salary_type": "estimated",
            "is_salary_estimated": True,
            "posted_time": time_posted,
            "description": desc,
            "skills": template["skills"],
            "is_urgent": is_urgent,
            "is_easy_apply": is_easy_apply,
            "linkedin_url": f"https://www.linkedin.com/jobs/view/{random.randint(3800000000, 3999999999)}",
            "is_fallback": True
        })

        if len(jobs) >= limit:
            break

    if not jobs and kw_lower:
        for idx, comp in enumerate(COMPANIES[:limit]):
            job_id = f"mock-job-custom-{idx}"
            jobs.append({
                "id": job_id,
                "title": f"Senior {keywords.title()} Specialist",
                "company_name": comp["name"],
                "company_logo": comp["logo"],
                "company_rating": comp["rating"],
                "company_size": comp["size"],
                "location": location if location else "Bengaluru, India",
                "workplace_type": "Remote" if "remote" in (location or "").lower() else "Hybrid",
                "job_type": "Full-time",
                "experience_level": "Mid-Senior level",
                "salary": "₹22L - ₹38L / yr",
                "salary_type": "estimated",
                "is_salary_estimated": True,
                "posted_time": "1 day ago",
                "description": f"We are looking for an experienced {keywords.title()} expert to join our core team. You will lead design, implementation, and cross-functional delivery of key projects.\n\nKey Responsibilities:\n- Drive technical execution for {keywords}.\n- Work with agile teams to deliver high quality solutions.\n\nRequirements:\n- 3+ years experience with {keywords}.\n- Strong analytical and problem-solving skills.",
                "skills": [keywords.title(), "Problem Solving", "Team Leadership", "Git", "Agile"],
                "is_urgent": True,
                "is_easy_apply": True,
                "linkedin_url": f"https://www.linkedin.com/jobs/view/{random.randint(3800000000, 3999999999)}",
                "is_fallback": True
            })

    return jobs
