import re
from datetime import datetime
SKILLS = ["Python", "Django", "React", "SQL", "JavaScript"]

def extract_email(text):
    match = re.findall(r'\S+@\S+', text)
    return match[0] if match else None


def extract_phone(text):
    match = re.findall(r'\d{10}', text)
    return match[0] if match else None
def extract_skills(text):
    found = []
    for skill in SKILLS:
        if skill.lower() in text.lower():
            found.append({
                "name": skill,
                "category": "technical",
                "experience_years": None
            })
    return found
def extract_experience(text):
    match = re.findall(r'(\d+)\s*(years|year)', text.lower())
    return int(match[0][0]) if match else 0
def extract_education(text):
    degrees = re.findall(r'(B\.Tech|MCA|MBA|BSc|MSc|BE)', text, re.IGNORECASE)

    education = []
    for degree in degrees:
        education.append({
            "degree": degree,
            "field_of_study": "",
            "institution": "",
            "end_year": ""
        })
    return education

def parse_resume(text, candidate_id=None, resume_id=None):

    structured_json = {

        "resume_id": resume_id,
        "candidate_id": candidate_id,

        "personal_info": {
            "full_name": "",
            "email": extract_email(text),
            "phone": extract_phone(text),
            "location": "",
            "linkedin": "",
            "github": ""
        },

        "skills": extract_skills(text),

        "experience": [],

        "education": extract_education(text),

        "total_experience_years": extract_experience(text),

        "parser_metadata": {
            "parser_version": "1.0",
            "parsed_at": str(datetime.now()),
            "confidence_score": 0.90
        }
    }

    return structured_json