from django.db import models

# Create your models here.
class PipelineStage(models.Model):
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name
    
class Application(models.Model):

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
    ]

    candidate = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='applications'
    )

    job = models.ForeignKey(
    'jobs.Job',
    on_delete=models.CASCADE,
    related_name='ats_applications'   # ✅ unique name
    )
    

    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.PROTECT
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('candidate', 'job')
    
    def move_stage(self, new_stage, user):

    
    # 🔐 Final stage lock
        if self.stage.is_final:
            raise ValueError("Application is locked")

    # 🔐 Employer ownership check
        if self.job.employer != user:
            raise ValueError("Not authorized")

    # 🔄 Prevent backward movement (optional rule)
        if new_stage.order < self.stage.order:
            raise ValueError("Cannot move backward")

        old_stage = self.stage
        self.stage = new_stage
        self.save()

    # 📝 Audit log
        ApplicationStatusHistory.objects.create(
            application=self,
            old_status=old_stage.name,
            new_status=new_stage.name,
            changed_by=user
        )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    # ✅ Allowed transitions
    ALLOWED_TRANSITIONS = {
    'applied': ['shortlisted', 'rejected'],
    'shortlisted': ['interview', 'rejected'],
    'interview': ['offered', 'rejected'],
    'offered': ['hired', 'rejected'],
    'hired': [],
    'rejected': [],
    'withdrawn': [],
}

def can_transition(self, new_status):
    return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

def update_status(self, new_status):
    # 🚫 Locked final stages
    if self.status in ['hired', 'rejected']:
        raise ValueError("Final stage cannot be modified")

    if not self.can_transition(new_status):
        raise ValueError(
            f"Invalid transition from {self.status} to {new_status}"
        )

    self.status = new_status
    self.save()
    
def change_status(self, new_status, user=None):
    allowed_transitions = {
        "applied": ["shortlisted", "rejected"],
        "shortlisted": ["interview", "rejected"],
        "interview": ["selected", "rejected"],
        "selected": [],
        "rejected": [],
    }

    if new_status in allowed_transitions[self.status]:

        old_status = self.status
        self.status = new_status
        self.save()

        # Create audit log
        ApplicationStatusHistory.objects.create(
            application=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            action="status_update"
        )

    else:
        raise ValueError("Invalid status transition")
    
class ApplicationStatusHistory(models.Model):
    ACTION_CHOICES = [
        ("status_update", "Status Update"),
        ("created", "Application Created"),
        ("note_added", "Note Added"),
    ]
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='history'
    )

    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)

    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

