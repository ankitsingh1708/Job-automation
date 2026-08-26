import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from app.services.scraper import search_linkedin_jobs, get_job_details
from app.services.mock_data import generate_mock_jobs

async def test_all():
    print("Testing mock generator...")
    mock_jobs = generate_mock_jobs("Software Engineer", "Remote", limit=5)
    assert len(mock_jobs) > 0, "Mock jobs should return at least 1 job"
    assert "title" in mock_jobs[0]
    print(f"Mock generator passed! Generated {len(mock_jobs)} jobs.")

    print("\nTesting LinkedIn search service...")
    search_res = await search_linkedin_jobs(keywords="Python Developer", location="Remote", limit=5)
    assert "jobs" in search_res
    assert len(search_res["jobs"]) > 0
    print(f"Search passed! Found {len(search_res['jobs'])} jobs (Source: {search_res['source']})")

    first_job_id = search_res["jobs"][0]["id"]
    print(f"\nTesting Job Details for job ID: {first_job_id}...")
    details = await get_job_details(first_job_id)
    assert details is not None
    assert "title" in details
    print(f"Job Details passed! Title: {details['title']}")

    print("\nAll service tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_all())
