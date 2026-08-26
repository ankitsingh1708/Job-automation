import os
import io
import csv
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.scraper import search_linkedin_jobs, get_job_details
from app.services.mock_data import COMPANIES, JOB_TEMPLATES
from app.services.resume_parser import (
    extract_text_from_pdf,
    parse_resume_text,
    calculate_job_match,
    generate_custom_cover_letter
)
from app.services.profile_store import load_profile, save_profile, record_question_answer
from app.services.auto_applier import (
    start_auto_apply_task,
    get_session,
    answer_session_question
)

app = FastAPI(
    title="LinkedIn Job Openings Portal & AI Resume Matcher",
    description="Fast, real-time LinkedIn job postings aggregator with intelligent search & AI resume matching.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ResumeTextPayload(BaseModel):
    text: str

class MatchPayload(BaseModel):
    resume_profile: Dict[str, Any]
    job: Dict[str, Any]

class CoverLetterPayload(BaseModel):
    resume_profile: Dict[str, Any]
    job: Dict[str, Any]

class StartApplyPayload(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    apply_url: str
    candidate_skills: Optional[List[str]] = []
    experience_years: Optional[int] = 4

class AnswerPayload(BaseModel):
    answer: str

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/jobs/search")
async def search_jobs(
    keywords: str = Query(""),
    location: str = Query(""),
    remote: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    date_posted: Optional[str] = None,
    exclude_service_companies: bool = False,
    top_tier_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50)
):
    return await search_linkedin_jobs(
        keywords=keywords,
        location=location,
        remote=remote,
        job_type=job_type,
        experience_level=experience_level,
        date_posted=date_posted,
        exclude_service_companies=exclude_service_companies,
        top_tier_only=top_tier_only,
        page=page,
        limit=limit
    )

@app.get("/api/jobs/{job_id}")
async def job_detail(job_id: str):
    job = await get_job_details(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job

@app.post("/api/resume/parse-file")
async def resume_parse_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF or TXT resume files are supported")
    
    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        raw_text = extract_text_from_pdf(content)
    else:
        raw_text = content.decode("utf-8", errors="ignore")
    
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
    
    return parse_resume_text(raw_text)

@app.post("/api/resume/parse-text")
async def resume_parse_text(payload: ResumeTextPayload):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Empty resume text provided")
    return parse_resume_text(payload.text)

@app.post("/api/resume/match")
async def resume_match(payload: MatchPayload):
    return calculate_job_match(payload.resume_profile, payload.job)

@app.post("/api/resume/cover-letter")
async def create_cover_letter(payload: CoverLetterPayload):
    return generate_custom_cover_letter(payload.resume_profile, payload.job)

# ----------------- Auto-Apply Endpoints ----------------- #

@app.get("/api/apply/profile")
async def get_candidate_profile():
    return load_profile()

@app.post("/api/apply/profile")
async def update_candidate_profile(profile: Dict[str, Any] = Body(...)):
    return save_profile(profile)

@app.post("/api/apply/start")
async def start_apply(payload: StartApplyPayload):
    session_id = start_auto_apply_task(
        job_id=payload.job_id,
        job_title=payload.job_title,
        company_name=payload.company_name,
        apply_url=payload.apply_url,
        candidate_skills=payload.candidate_skills,
        experience_years=payload.experience_years,
        headless=False
    )
    return {"session_id": session_id, "status": "STARTED"}

@app.get("/api/apply/session/{session_id}")
async def get_apply_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.session_id,
        "job_id": session.job_id,
        "job_title": session.job_title,
        "company_name": session.company_name,
        "status": session.status,
        "logs": session.logs,
        "pending_question": session.pending_question,
        "error_message": session.error_message
    }

@app.post("/api/apply/session/{session_id}/answer")
async def answer_apply_session(session_id: str, payload: AnswerPayload):
    success = answer_session_question(session_id, payload.answer)
    if not success:
        raise HTTPException(status_code=400, detail="Could not submit answer. Session may not be waiting for input.")
    return {"status": "ANSWER_SUBMITTED"}

# ----------------- Stats & Export ----------------- #

@app.get("/api/stats")
async def get_platform_stats():
    trending_roles = [
        {"role": "Python Backend Engineer", "growth": "+42%", "openings": "4,200+"},
        {"role": "AI / GenAI & LLM Specialist", "growth": "+88%", "openings": "2,850+"},
        {"role": "Full Stack Developer (React/FastAPI)", "growth": "+34%", "openings": "5,100+"},
        {"role": "DevOps & Cloud SRE", "growth": "+29%", "openings": "3,400+"},
        {"role": "Data Scientist & ML", "growth": "+25%", "openings": "2,600+"},
    ]
    popular_skills = ["Python", "FastAPI", "React", "AWS", "Kubernetes", "SQL", "Docker", "Machine Learning", "TypeScript", "Go"]
    top_hiring_companies = [c["name"] for c in COMPANIES[:8]]
    location_distribution = [
        {"location": "Bengaluru, India", "percentage": 38},
        {"location": "Hyderabad, India", "percentage": 22},
        {"location": "Pune, India", "percentage": 15},
        {"location": "Delhi NCR, India", "percentage": 14},
        {"location": "Remote, India", "percentage": 11},
    ]

    return {
        "trending_roles": trending_roles,
        "popular_skills": popular_skills,
        "top_companies": top_hiring_companies,
        "location_distribution": location_distribution,
        "avg_salary_range": "₹16 LPA - ₹38 LPA"
    }

@app.get("/api/export")
async def export_jobs(
    keywords: str = Query(""),
    location: str = Query(""),
    remote: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    date_posted: Optional[str] = None,
    exclude_service_companies: bool = False,
    format: str = Query("csv", pattern="^(csv|json)$")
):
    results = await search_linkedin_jobs(
        keywords=keywords,
        location=location,
        remote=remote,
        job_type=job_type,
        experience_level=experience_level,
        date_posted=date_posted,
        exclude_service_companies=exclude_service_companies,
        page=1,
        limit=50
    )
    jobs = results.get("jobs", [])

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Title", "Company", "Location", "Workplace", "Type", "Salary", "Posted", "Apply URL"])
        for j in jobs:
            writer.writerow([
                j.get("id", ""),
                j.get("title", ""),
                j.get("company_name", ""),
                j.get("location", ""),
                j.get("workplace_type", ""),
                j.get("job_type", ""),
                j.get("salary", ""),
                j.get("posted_time", ""),
                j.get("linkedin_url", "")
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=linkedin_job_openings.csv"}
        )

    return jobs
