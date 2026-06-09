from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = (
        ('TEACHER', 'Teacher'),
        ('COUNSELOR', 'Counselor'),
        ('PRINCIPAL', 'Principal'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TEACHER')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='school_app_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='school_app_user_permissions',
        blank=True
    )

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    grade_level = models.CharField(max_length=20, db_index=True)
    assigned_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'TEACHER'}, db_index=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    is_absent = models.BooleanField(default=False)
    behavioral_flag = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. 'seems withdrawn'")
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {'Absent' if self.is_absent else 'Present'}"

class InterventionCase(models.Model):
    STATUS_CHOICES = (
        ('NEW', 'New Alert'),
        ('IN_REVIEW', 'In Review'),
        ('INTERVENTION', 'Intervention Planned'),
        ('FOLLOW_UP_MISSED', 'Missed Follow-up'),
        ('RESOLVED', 'Resolved'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='interventions')
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'COUNSELOR'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW', db_index=True)
    risk_score = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    plan_description = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)

    def clean(self):
        if self.status == 'RESOLVED' and not self.resolution_notes:
            raise ValidationError("Resolution notes are required when closing a case.")

    def __str__(self):
        return f"Case: {self.student} ({self.get_status_display()})"

class SystemConfiguration(models.Model):
    absence_threshold = models.IntegerField(default=3, help_text="Number of consecutive absences before alerting.")
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"

    def __str__(self):
        return f"Config (Threshold: {self.absence_threshold})"

class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_role = models.CharField(max_length=20, blank=True, null=True)
    case = models.ForeignKey(InterventionCase, on_delete=models.CASCADE, related_name='action_logs', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action_detail = models.CharField(max_length=255)
    result = models.CharField(max_length=50, default='Success')

    def __str__(self):
        return f"{self.timestamp} - {self.user} ({self.user_role}) - {self.action_detail} ({self.result})"
