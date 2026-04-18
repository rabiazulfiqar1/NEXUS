from app.core.config import CRON_QUERIES, COUNTRY, EMPLOYMENT_TYPES, JOB_SEARCH_API
import requests
from app.schemas.job import JobCreate
from datetime import datetime
from app.db.database import add_jobs, embed_jobs

JOB_SEARCH_URL="https://jsearch.p.rapidapi.com/search"
PARAMETERS = {
    "country": COUNTRY,
    "employment_types": EMPLOYMENT_TYPES
}
headers = {
    "x-rapidapi-key": JOB_SEARCH_API,
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
    "Content-Type": "application/json"
}

def fetch_jobs():
    job_list = []
    for query in CRON_QUERIES:
        try:
            PARAMETERS["query"] = query
            response = requests.get(JOB_SEARCH_URL, params=PARAMETERS, headers=headers).json()
            for job in response["data"]:
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
