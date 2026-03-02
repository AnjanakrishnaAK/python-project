def calculate_skills_score(candidate_skills, required_skills, preferred_skills):
    candidate = set([s.lower() for s in candidate_skills])
    required = set([s.lower() for s in required_skills])
    preferred = set([s.lower() for s in preferred_skills])

    required_match = len(candidate & required)
    preferred_match = len(candidate & preferred)

    score = 0
    if required:
        score += (required_match / len(required)) * 70

    if preferred:
        score += (preferred_match / len(preferred)) * 30

    return score
def calculate_experience_score(candidate_exp, min_exp, max_exp):

    if candidate_exp < min_exp:
        return (candidate_exp / min_exp) * 100

    elif candidate_exp <= max_exp:
        return 100

    return (max_exp / candidate_exp) * 100
def calculate_education_score(candidate_education, required_education):

    candidate_education = candidate_education.lower()

    for edu in required_education:
        if edu.lower() in candidate_education:
            return 100

    return 50