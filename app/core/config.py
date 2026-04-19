import os
from dotenv import load_dotenv

load_dotenv()

JOB_SEARCH_API = os.getenv("JOB_SEARCH_API")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")

CRON_QUERIES = [
    "software engineering Jobs in Pakistan",
    # "data science Jobs in Pakistan",
    # "machine learning Jobs in Pakistan",
    # "backend developer Jobs in Pakistan",
    # "frontend developer Jobs in Pakistan",
    # "cybersecurity Jobs in Pakistan",
]
COUNTRY="pk"
EMPLOYMENT_TYPES="PARTTIME,INTERN"

ALLOWED_FILE_TYPES = ['application/pdf']

MATCH_THRESHOLD = 0.4
MATCH_COUNT=5

