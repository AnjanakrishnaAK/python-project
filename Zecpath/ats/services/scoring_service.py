from ats.models import ATSScore
from ats.services.engine import calculate_skills_score,calculate_experience_score,calculate_education_score

class ATSScoringService:
    @staticmethod
    def calculate(candidate, job):
        skills = calculate_skills_score(
            candidate.skills,
            job.required_skills,
            job.preferred_skills
        )
        experience = calculate_experience_score(
            candidate.experience,
            job.min_experience,
            job.max_experience
        )
        education = calculate_education_score(
            candidate.education,
            job.required_education
        )
        total = (
            (skills * 0.5) +
            (experience * 0.3) +
            (education * 0.2)
        )
        score_obj, created = ATSScore.objects.update_or_create(
            candidate=candidate,
            job=job,
            defaults={
                "skills_score": skills,
                "experience_score": experience,
                "education_score": education,
                "total_score": round(total, 2)
            }
        )
        return score_obj
    @staticmethod
    def rank_candidates(job):

        return ATSScore.objects.filter(
            job=job
        ).order_by("-total_score")