import os
import django
import random
from faker import Faker
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educare_project.settings')
django.setup()

from school_app.models import User, Student, AttendanceRecord, InterventionCase

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

    print("Creating students...")
    students = []
    for _ in range(15):
        student = Student.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_birth=fake.date_of_birth(minimum_age=12, maximum_age=18),
            grade_level=random.choice(["7th Grade", "8th Grade", "9th Grade"]),
            assigned_teacher=teacher
        )
        students.append(student)

    print("Creating attendance records and interventions...")
    for student in students:
        # Simulate some random attendance records
        for i in range(5):
            date = fake.date_between(start_date='-30d', end_date='today')
            # 20% chance of absence
            is_absent = random.random() < 0.2
            
            # Avoid IntegrityError by using get_or_create for unique_together
            record, created = AttendanceRecord.objects.get_or_create(
                student=student,
                date=date,
                defaults={
                    'is_absent': is_absent,
                    'logged_by': teacher,
                    'behavioral_flag': 'seems withdrawn' if random.random() < 0.1 else ''
                }
            )

        # Generate a fake intervention for some students
        if random.random() < 0.3:
            InterventionCase.objects.create(
                student=student,
                counselor=counselor,
                status=random.choice(['NEW', 'IN_REVIEW', 'INTERVENTION']),
                risk_score=random.randint(50, 95),
                plan_description="Needs regular check-ins.",
            )

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
