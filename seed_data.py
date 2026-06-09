import os
import django
import random
from faker import Faker
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educare_project.settings')
django.setup()

from school_app.models import User, Student, AttendanceRecord, InterventionCase, SystemConfiguration

fake = Faker()

def seed_data():
    print("Clearing database...")
    InterventionCase.objects.all().delete()
    AttendanceRecord.objects.all().delete()
    Student.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    print("Creating users...")
    teacher = User.objects.create_user(username='teacher1', password='password123', role='TEACHER', first_name='John', last_name='Doe')
    counselor = User.objects.create_user(username='counselor1', password='password123', role='COUNSELOR', first_name='Jane', last_name='Smith')
    principal = User.objects.create_user(username='admin1', password='password123', role='PRINCIPAL', first_name='Boss', last_name='Man')

    print("Creating students for teacher1...")
    students = []
    # Create 10 students all assigned to teacher1 to ensure consistent demo
    for _ in range(10):
        student = Student.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_birth=fake.date_of_birth(minimum_age=12, maximum_age=18),
            grade_level=random.choice(["7th Grade", "8th Grade", "9th Grade"]),
            assigned_teacher=teacher
        )
        students.append(student)

    print("Generating consistent scenario data...")
    today = timezone.now().date()
    
    # Ensure at least ONE student has 3 consecutive absences (Threshold Alert)
    absentee_student = students[0]
    for i in range(3):
        AttendanceRecord.objects.create(
            student=absentee_student,
            date=today - timedelta(days=i+1),
            is_absent=True,
            logged_by=teacher
        )
    # Manually trigger the alert that views.py would usually handle
    InterventionCase.objects.create(
        student=absentee_student,
        status='NEW',
        risk_score=85,
        plan_description="Automated alert: 3 consecutive absences detected."
    )

    # Ensure at least ONE student has a behavioral flag (Scenario 1 Alert)
    flagged_student = students[1]
    AttendanceRecord.objects.create(
        student=flagged_student,
        date=today - timedelta(days=1),
        is_absent=False,
        behavioral_flag="Appears extremely lethargic and disengaged in class.",
        logged_by=teacher
    )
    InterventionCase.objects.create(
        student=flagged_student,
        status='NEW',
        risk_score=75,
        plan_description=f"Automated alert: Behavioral flag logged by teacher1: Appears extremely lethargic and disengaged in class."
    )

    # Ensure at least ONE student has an ongoing intervention (Scenario 2 Follow-up)
    intervention_student = students[2]
    case = InterventionCase.objects.create(
        student=intervention_student,
        counselor=counselor,
        status='INTERVENTION',
        risk_score=60,
        plan_description="Scheduled weekly check-ins with family.",
        follow_up_date=today + timedelta(days=7)
    )

    # Create random historical data for the rest
    for student in students[3:]:
        for i in range(5):
            AttendanceRecord.objects.get_or_create(
                student=student,
                date=today - timedelta(days=i+1),
                defaults={
                    'is_absent': random.random() < 0.1,
                    'logged_by': teacher
                }
            )

    print("Database seeded with consistent cross-role data!")

if __name__ == '__main__':
    seed_data()
