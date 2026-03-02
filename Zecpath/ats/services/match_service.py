class MatchService:

    @staticmethod
    def calculate(candidate, job):
        candidate_skills = set(candidate.skills.values_list("name", flat=True))
        job_skills = set(job.required_skills.values_list("name", flat=True))

        matched = candidate_skills.intersection(job_skills)
        missing = job_skills.difference(candidate_skills)

        # Skill score
        if len(job_skills) > 0:
            skill_score = (len(matched) / len(job_skills)) * 100
        else:
            skill_score = 0

        # Experience check
        experience_match = candidate.years_of_experience >= job.required_experience

        final_score = round(skill_score)

        return {
            "match_percentage": final_score,
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "experience_match": experience_match
        }