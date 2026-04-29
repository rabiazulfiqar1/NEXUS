from crewai import Agent
from app.services.crew.llm import get_crew_llm
from app.services.crew.tools import (
    FetchProfileTool,
    FetchMatchedJobsTool,
    ATSBatchScoreTool,
    # ATSScoreTool,
    EnhanceResumeTool,
    MarketResearchTool,
)

def build_agents():
    llm = get_crew_llm()

    profile_analyst = Agent(
        role="Profile Analyst",
        goal=(
            "Produce a precise gap analysis of the candidate's profile — "
            "strengths, skill gaps, and ATS scores against matched jobs."
        ),
        backstory=(
            "You are an expert career coach who has reviewed thousands of resumes. "
            "You are data-driven and back every claim with ATS scores and specific job requirements."
        ),
        tools=[FetchProfileTool(), FetchMatchedJobsTool(), ATSBatchScoreTool()],
        llm=llm,
        verbose=True,
        memory=True,
    )

    market_researcher = Agent(
        role="Job Market Researcher",
        goal=(
            "Surface exactly which skills are trending for the target role right now "
            "and map them precisely against the candidate's identified gaps."
        ),
        backstory=(
            "You track live hiring trends. You know which skills are rising, "
            "which are declining, and what the market is actively paying for right now."
        ),
        tools=[MarketResearchTool()],
        llm=llm,
        verbose=True,
        memory=True,
    )

    resume_enhancer = Agent(
        role="Resume Enhancer",
        goal=(
            "Rewrite the candidate's resume bullets and summary using real skill gaps "
            "and live market trends. Never invent experience — only reframe what exists."
        ),
        backstory=(
            "You are a professional resume writer specialising in ATS optimisation. "
            "You transform generic bullets into specific, impact-driven statements "
            "that pass ATS filters and impress hiring managers."
        ),
        tools=[EnhanceResumeTool()],
        llm=llm,
        verbose=True,
        memory=True,
    )

    cv_generator = Agent(
        role="CV Generator",
        goal=(
            "Produce a complete, tailored, ATS-optimised CV for the target role "
            "using only verified profile data and the enhanced resume content."
        ),
        backstory=(
            "You are a senior technical recruiter who builds CVs that get interviews. "
            "You order skills strategically, write tight summaries, and are ruthlessly "
            "honest about remaining gaps — because candidates need to know what to fix next."
        ),
        tools=[],
        llm=llm,
        verbose=True,
    )

    return profile_analyst, market_researcher, resume_enhancer, cv_generator