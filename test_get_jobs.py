import asyncio
from app.db.database import get_jobs


async def main():
    user_id = "0dd1ef99-90cf-4fcd-8cca-1c3415ed002c"

    try:
        jobs = await get_jobs(user_id)

        print("\n=== JOB RESULTS ===")
        if not jobs:
            print("No jobs found.")
        else:
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job}")

    except Exception as e:
        print("\n=== ERROR ===")
        print(str(e))


if __name__ == "__main__":
    asyncio.run(main())