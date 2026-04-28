from app.core.config import CRON_QUERIES, COUNTRY, EMPLOYMENT_TYPES, JOB_SEARCH_API
from app.schemas.job import JobCreate
from datetime import datetime
from app.db.database import add_jobs, embed_jobs
import aiohttp

JOB_SEARCH_URL="https://jsearch.p.rapidapi.com/search"
BASE_PARAMETERS = {
    "country": COUNTRY,
    "employment_types": EMPLOYMENT_TYPES
}
headers = {
    "x-rapidapi-key": JOB_SEARCH_API,
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
    "Content-Type": "application/json"
}

async def fetch_jobs():
    job_list: list[JobCreate] = []
    async with aiohttp.ClientSession() as session:
        for query in CRON_QUERIES:
            params = {**BASE_PARAMETERS, "query": query}
            try:
                async with session.get(JOB_SEARCH_URL, params=params, headers=headers) as response:
                    response.raise_for_status()
                    payload = await response.json()
                for job in payload.get("data", []):
                    job_data = JobCreate(
                        title=job["job_title"],
                        company=job["employer_name"],
                        location=job.get("job_location"),
                        employment_type=job.get("job_employment_type"),
                        source=job.get("job_publisher"),      
                        description=job["job_description"],    
                        url=job["job_apply_link"],
                        posted_at=datetime.fromtimestamp(job.get("job_posted_at_timestamp"))
                                if job.get("job_posted_at_timestamp") else None
                    )
                    print(job_data)
                    job_list.append(job_data)
            except Exception as e:
                print(f"Failed for query: '{query}': {e}")
                continue
    add_jobs(job_list)
    embed_jobs(job_list)
