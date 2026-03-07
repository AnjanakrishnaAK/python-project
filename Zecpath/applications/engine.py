from .services.eligibility_service import EligibilityService

ROLE_THRESHOLDS = {
    "intern": 55,
    "junior": 65,
    "mid": 70,
    "senior": 80,
}
def skill_match(candidate_skills, required_skills):
    if not required_skills:
        return 0

    matched = set(candidate_skills).intersection(set(required_skills))
    return (len(matched) / len(required_skills)) * 100

def experience_match(candidate_exp, required_exp):
    if candidate_exp >= required_exp:
        return 100
    return (candidate_exp / required_exp) * 100

def hard_filter(candidate_profile, job):

    if not set(job.mandatory_skills).issubset(
        set(candidate_profile.skills)
    ):
        return False

    if candidate_profile.experience < job.min_experience:
        return False

    return True

def auto_shortlist_engine(application):
    if application.overridden:
        return
    candidate_profile = application.candidate.profile
    job = application.job
# Hard filter check
    if not hard_filter(candidate_profile, job):
        application.status = "rejected"
        application.auto_processed = True
        application.save()
        return
# Calculate score
    skill_score = skill_match(candidate_profile.skills,job.required_skills)
    exp_score = experience_match(candidate_profile.experience,job.min_experience)
    final_score = (skill_score * 0.6) + (exp_score * 0.4)
    application.match_score = round(final_score, 2)
# Role-based threshold
    base_threshold = ROLE_THRESHOLDS.get(job.role_level, 70)
# Dynamic adjustment based on applicant count
    applicant_count = job.applications.count()
    if applicant_count > 200:
        base_threshold += 5
    elif applicant_count < 10:
        base_threshold -= 5
# Decision
    if final_score >= base_threshold:
        application.status = "shortlisted"
    elif final_score <= 40:
        application.status = "rejected"
    else:
        application.status = "review"
    application.score_breakdown = {"skills": skill_score,"experience": exp_score,"threshold": base_threshold}
    application.auto_processed = True
    application.save()

def auto_shortlist_engine(application):

    if not EligibilityService.is_eligible(application):
        application.status = "rejected"
        application.save()
        return

    application.status = "shortlisted"
    application.save()