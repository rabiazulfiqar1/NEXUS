from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from app.core.dependencies import get_current_user
from app.core.rate_limiter import rate_limit
from app.services.crew.career_crew import run_career_analysis
from app.services.crew.tasks import GeneratedCV
from app.db.async_client import get_async_client
from app.services.cv_exporter import export_cv_to_pdf
from fastapi.responses import Response
import asyncio

router = APIRouter()

CREW_TIMEOUT = 300  # 5 minutes

@router.post("/career/analyze", response_model=GeneratedCV)
async def analyze_career(
    request: Request,
    target_role: str,
    user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit("career_analyze")),
):
    if not target_role.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_role is required.",
        )

    try:
        cv = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: asyncio.run(run_career_analysis(str(user.id), target_role.strip()))
            ),
            timeout=CREW_TIMEOUT,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Analysis timed out after {CREW_TIMEOUT}s. Try a more specific role or try again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )

    return cv


@router.get("/career/cv/latest", response_model=GeneratedCV)
async def get_latest_cv(user: dict = Depends(get_current_user)):
    client = await get_async_client()
    result = await client.table("career_reports") \
        .select("report, target_role, created_at") \
        .eq("user_id", str(user.id)) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No CV generated yet. Run /career/analyze first.",
        )
    return GeneratedCV(**result.data[0]["report"])


@router.get("/career/cv/export")
async def export_cv(user: dict = Depends(get_current_user)):
    client = await get_async_client()
    result = await client.table("career_reports") \
        .select("report") \
        .eq("user_id", str(user.id)) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No CV found. Run /career/analyze first.",
        )
    cv        = GeneratedCV(**result.data[0]["report"])
    pdf_bytes = export_cv_to_pdf(cv, candidate_name=user.email)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cv.pdf"},
    )