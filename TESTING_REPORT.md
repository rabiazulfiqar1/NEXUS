# Testing Report

Project: NEXUS
Command: `python -m pytest tests/ -v --tb=short`

## Result

- Total tests run: 133
- Passed: 131
- Skipped: 2
- Failed: 0

## Breakdown by test file (module)

- **test_api_career.py**: Passed=7, Failed=0, Error=0, Skipped=0
- **test_api_jobs.py**: Passed=5, Failed=0, Error=0, Skipped=0
- **test_api_resume_tools.py**: Passed=8, Failed=0, Error=0, Skipped=0
- **test_api_users.py**: Passed=8, Failed=0, Error=0, Skipped=0
- **test_career_crew.py**: Passed=7, Failed=0, Error=0, Skipped=0
- **test_database.py**: Passed=11, Failed=0, Error=0, Skipped=0
- **test_embedding.py**: Passed=6, Failed=0, Error=0, Skipped=0
- **test_integration.py**: Passed=2, Failed=0, Error=0, Skipped=2
- **test_job_fetcher.py**: Passed=3, Failed=0, Error=0, Skipped=0
- **test_llm_resume.py**: Passed=33, Failed=0, Error=0, Skipped=0
- **test_rate_limiter.py**: Passed=8, Failed=0, Error=0, Skipped=0
- **test_resume_parser.py**: Passed=14, Failed=0, Error=0, Skipped=0
- **test_schemas.py**: Passed=19, Failed=0, Error=0, Skipped=0

## Notes

- The skipped tests are live Groq integration tests and are skipped when `GROQ_API_KEY` is not set.
- The suite completed successfully with no failing tests.

## Validation

- Full test suite completed successfully in approximately 64.6 seconds.
