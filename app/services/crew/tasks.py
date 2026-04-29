from crewai import Task
from pydantic import BaseModel
from app.services.crew.agents import build_agents

# ── Output schemas ────────────────────────────────────────────────────────────

class EnhancedResume(BaseModel):
    summary:          str
    improved_bullets: list[str]
    missing_keywords: list[str]
    next_steps:       list[str]

class GeneratedCV(BaseModel):
    professional_summary:  str
    skills:                list[str]
    experience_bullets:    list[str]
    projects:              list[str]
    ats_score:             float
    trending_skills_used:  list[str]
    skill_gaps_remaining:  list[str]


# ── Task builder ──────────────────────────────────────────────────────────────

def build_tasks(user_id: str, target_role: str) -> list[Task]:
    profile_analyst, market_researcher, resume_enhancer, cv_generator = build_agents()

    task_1 = Task(
        description=f"""
        You MUST follow these steps in order:

        Step 1: Call fetch_user_profile with user_id="{user_id}".
        Step 2: Call fetch_matched_jobs with user_id="{user_id}".
            The tool returns a list of job objects. Each job has an "id" field
            (or "job_id" if "id" is missing).
            Extract the "id" value from the first job in the list.
        Step 3: Call compute_ats_scores_batch with:
                - user_id="{user_id}"
                - job_ids = the exact "id" value you extracted in Step 2
                Do NOT use placeholder IDs like 'job1', 'job2', 'job3'.
                ONLY use real IDs from the fetch_matched_jobs response.

        Then identify:
        - Current strengths
        - Skill gaps vs matched job requirements
        - ATS score for the top matched job
        - Specific unmet job requirements
        """,
        expected_output=(
            "Profile summary containing: strengths list, skill gaps list, "
            "average ATS score (float 0-1), unmet job requirements list."
        ),
        agent=profile_analyst,
    )

    task_2 = Task(
        description=f"""
        Research current market demands for: {target_role} in 2025.
        Cross-reference with the skill gaps identified in task 1.

        Produce:
        - Top 3 trending skills for {target_role} right now
        - Which trending skills overlap with the candidate's gaps (highest priority)
        - Which trending skills the candidate already has
        - Skills that are declining — candidate should deprioritise these
        """,
        expected_output=(
            "Trending skills list, gap-trend overlap list (prioritised), "
            "skills already present, skills to deprioritise."
        ),
        agent=market_researcher,
        context=[task_1],
    )

    task_3 = Task(
        description=f"""
        Using skill gaps from task 1 and trending skills from task 2,
        enhance the candidate's resume for role: {target_role}.

        You must:
        - Rewrite weak bullets to incorporate trending keywords naturally
        - Surface missing keywords the candidate should add
        - Prioritise next steps by gap-trend overlap (highest ROI first)
        - Write a strong professional summary targeting {target_role}

        Do NOT invent experience. Only reframe what exists using stronger language and keywords.
        """,
        expected_output=(
            "Improved bullets list, missing keywords list, "
            "prioritised next steps, professional summary string."
        ),
        agent=resume_enhancer,
        context=[task_1, task_2],
        output_pydantic=EnhancedResume,
    )

    task_4 = Task(
        description=f"""
        Generate a complete tailored CV for role: {target_role}.

        Use ONLY information grounded in the profile and enhanced resume from task 3.
        Incorporate trending skills from task 2 where genuinely present in the profile.

        Produce:
        - Sharp professional summary (3-4 sentences max)
        - Skills ordered by relevance to {target_role} (trending skills first)
        - Experience bullets (use improved bullets from task 3)
        - Projects section (only real projects from the profile)
        - trending_skills_used: which trends were successfully incorporated
        - skill_gaps_remaining: honest gaps still present after enhancement
        - ats_score: estimated score (0.0-1.0) of this CV vs matched jobs

        Do NOT invent companies, roles, or projects.
        """,
        expected_output="Complete GeneratedCV with ATS score and gap analysis.",
        agent=cv_generator,
        context=[task_1, task_2, task_3],
        output_pydantic=GeneratedCV,
    )

    return [task_1, task_2, task_3, task_4]