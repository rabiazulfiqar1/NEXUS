import pdfplumber

def extract_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            # print(page.extract_text())

    return text

def build_user_embedding_text(profile: dict) -> str:
    skills_text = " ".join(profile.get("skills") or [])
    degree_text = profile.get("degree") or ""
    experience_text = ""
    for exp in profile.get("experience") or []:
        for key, val in exp.items():
            experience_text += f"{key}: {val} "
    
    return f"{skills_text} {degree_text} {experience_text}".strip()