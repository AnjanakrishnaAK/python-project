class ApplicationStatus:
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    SELECTED = "selected"

    CHOICES = [
        (APPLIED, "Applied"),
        (SHORTLISTED, "Shortlisted"),
        (INTERVIEW, "Interview Scheduled"),
        (REJECTED, "Rejected"),
        (SELECTED, "Selected"),
    ]