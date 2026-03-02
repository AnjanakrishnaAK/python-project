import re
import spacy
from .skills import SKILL_DATABASE



def extract_skills(text):

    text_lower = text.lower()

    found_skills = []

    for skill in SKILL_DATABASE:

        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))

    
def extract_skills_with_experience(text):

    skills = []

    for skill in SKILL_DATABASE:

        pattern = rf'(\d+)?\s*(years)?\s*(of)?\s*(experience)?\s*(in)?\s*{skill}'

        match = re.search(pattern, text.lower())

        if match:
            years = match.group(1) if match.group(1) else None

            skills.append({
                "name": skill,
                "experience_years": years
            })

    return skills

nlp = spacy.load("en_core_web_sm")
def extract_skills_nlp(text):

    doc = nlp(text)

    tokens = [token.text.lower() for token in doc]

    skills = []

    for skill in SKILL_DATABASE:
        if skill.lower() in tokens:
            skills.append(skill)

    return skills