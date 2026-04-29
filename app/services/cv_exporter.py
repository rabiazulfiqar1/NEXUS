from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.services.crew.tasks import GeneratedCV
import io

def export_cv_to_pdf(cv: GeneratedCV, candidate_name: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(candidate_name, styles["Title"]))
    story.append(Paragraph(cv.professional_summary, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Skills", styles["Heading2"]))
    story.append(Paragraph(", ".join(cv.skills), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Experience", styles["Heading2"]))
    for bullet in cv.experience_bullets:
        story.append(Paragraph(f"• {bullet}", styles["Normal"]))

    if cv.projects:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Projects", styles["Heading2"]))
        for project in cv.projects:
            story.append(Paragraph(f"• {project}", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()