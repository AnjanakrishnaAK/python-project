from accounts.models import Skill
from jobs.models import Job
from applications.models import Application


class EligibilityService:
    @staticmethod
    def check_experience(candidate_profile, job):
        """
        Check candidate experience eligibility
        """
        if not candidate_profile.experience_years:
            return False

        return (
            job.experience_min
            <= candidate_profile.experience_years
            <= job.experience_max
        )
    @staticmethod
    def check_skills(candidate_profile, job):
        """
        Check if candidate has required skills
        """
        job_skills = set(job.skills.values_list("name", flat=True))
        candidate_skills = set(
            candidate_profile.skills.values_list("name", flat=True)
        )

        matched = job_skills.intersection(candidate_skills)

        if not job_skills:
            return True

        match_percent = (len(matched) / len(job_skills)) * 100

        return match_percent >= 50

    @staticmethod
    def check_location(candidate_profile, job):
        """
        Optional location match
        """
        if not job.location:
            return True

        return candidate_profile.location == job.location

    @classmethod
    def is_eligible(cls, application):
        """
        Full eligibility check
        """

        candidate = application.candidate
        job = application.job

        exp_ok = cls.check_experience(candidate, job)
        skills_ok = cls.check_skills(candidate, job)
        location_ok = cls.check_location(candidate, job)

        return exp_ok and skills_ok and location_ok