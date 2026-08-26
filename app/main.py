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

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "linkedin-jobs-portal"}

@app.get("/api/jobs/search")
async def search_jobs(
    keywords: str = Query("", description="Search job title, skill, or company"),
    location: str = Query("", description="City, state, or country"),
    remote: Optional[str] = Query(None, description="Workplace type: remote, hybrid, on-site"),
    job_type: Optional[str] = Query(None, description="Job type: full-time, part-time, contract, internship"),
    experience_level: Optional[str] = Query(None, description="Experience: internship, entry, associate, mid-senior, director, executive"),
    date_posted: Optional[str] = Query(None, description="Time posted: 24h, week, month"),
    exclude_service_companies: bool = Query(False, description="Exclude Indian service-based & staffing companies"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(40, ge=1, le=100, description="Results per page")
):
    results = await search_linkedin_jobs(
        keywords=keywords,
        location=location,
        remote=remote,
        job_type=job_type,
        experience_level=experience_level,
        date_posted=date_posted,
        exclude_service_companies=exclude_service_companies,
        page=page,
        limit=limit
    )
    return results

@app.get("/api/jobs/{job_id}")
async def job_detail(job_id: str):
    details = await get_job_details(job_id)
    if not details:
        raise HTTPException(status_code=404, detail="Job opening not found")
    return details

@app.post("/api/resume/parse-file")
async def parse_resume_file(file: UploadFile = File(...)):
    contents = await file.read()
    filename = (file.filename or "").lower()
    
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(contents)
    else:
        try:
            text = contents.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from resume file.")

    profile = parse_resume_text(text)
    profile["filename"] = file.filename
    return profile

@app.post("/api/resume/parse-text")
async def parse_resume_text_endpoint(payload: ResumeTextPayload):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    profile = parse_resume_text(text)
    profile["filename"] = "Pasted Resume Text"
    return profile

@app.post("/api/resume/match")
async def match_resume_with_job(payload: MatchPayload):
    match_result = calculate_job_match(payload.resume_profile, payload.job)
    return match_result

@app.post("/api/resume/cover-letter")
async def generate_cover_letter(payload: CoverLetterPayload):
    letter = generate_custom_cover_letter(payload.resume_profile, payload.job)
    return {"cover_letter": letter}

@app.get("/api/stats")
async def get_market_stats():
    trending_roles = [t["title"] for t in JOB_TEMPLATES[:6]]
    popular_skills = ["Python", "React", "AWS", "Kubernetes", "SQL", "Docker", "Machine Learning", "TypeScript", "Go", "Terraform"]
    top_hiring_companies = [c["name"] for c in COMPANIES[:8]]
    location_distribution = [
        {"location": "Remote", "percentage": 42},
        {"location": "San Francisco, CA", "percentage": 18},
        {"location": "New York, NY", "percentage": 15},
        {"location": "Seattle, WA", "percentage": 10},
        {"location": "Austin, TX", "percentage": 8},
        {"location": "Other Tech Hubs", "percentage": 7},
    ]

    return {
        "trending_roles": trending_roles,
        "popular_skills": popular_skills,
        "top_companies": top_hiring_companies,
        "location_distribution": location_distribution,
        "avg_salary_range": "$130,000 - $190,000 / yr"
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
