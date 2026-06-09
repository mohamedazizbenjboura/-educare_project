from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Student, InterventionCase, AttendanceRecord

class EduCareTestCase(TestCase):
    def setUp(self):
        # Setup Users
        self.teacher = User.objects.create_user(username='t1', password='pw', role='TEACHER')
        self.counselor = User.objects.create_user(username='c1', password='pw', role='COUNSELOR')
        self.principal = User.objects.create_user(username='p1', password='pw', role='PRINCIPAL')
        
        # Setup Student
        self.student = Student.objects.create(
            first_name='Luke', last_name='Skywalker', 
            date_of_birth='2010-01-01', grade_level='9th', assigned_teacher=self.teacher
        )
        self.client = Client()

    def test_login_and_redirect(self):
        # Scenario 1 start: Teacher logs in
        self.client.login(username='t1', password='pw')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('teacher_dashboard'))

    def test_role_based_access_control(self):
        # Expected Failure: Teacher tries to access counselor dashboard
        self.client.login(username='t1', password='pw')
        response = self.client.get(reverse('counselor_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects properly denying view

    def test_intervention_creation_on_behavioral_flag(self):
        # Scenario 1 logic: Flag creates intervention
        self.client.login(username='t1', password='pw')
        today = timezone.now().date().isoformat()
        response = self.client.post(reverse('log_attendance', args=[self.student.id]), {
            'date': today,
            'is_absent': False,
            'behavioral_flag': 'Very disruptive today'
        })
        self.assertEqual(InterventionCase.objects.count(), 1)
        case = InterventionCase.objects.first()
        self.assertEqual(case.student, self.student)
        self.assertTrue("Very disruptive today" in case.plan_description)

    def test_case_resolution_validation(self):
        # Scenario 2 constraint: Closing case without notes fails
        case = InterventionCase.objects.create(student=self.student, status='IN_REVIEW')
        self.client.login(username='c1', password='pw')
        response = self.client.post(reverse('case_detail', args=[case.id]), {
            'status': 'RESOLVED',
            'plan_description': 'plan',
            'follow_up_date': '',
            'resolution_notes': '' # Blank, should fail
        })
        case.refresh_from_db()
        self.assertNotEqual(case.status, 'RESOLVED') # Status shouldn't change
        self.assertContains(response, 'Resolution notes are required when closing a case.')

    def test_future_date_attendance_fails(self):
        # Scenario 1 constraint: Future dates trigger validation failure
        self.client.login(username='t1', password='pw')
        future_date = (timezone.now() + timezone.timedelta(days=2)).date().isoformat()
        response = self.client.post(reverse('log_attendance', args=[self.student.id]), {
            'date': future_date,
            'is_absent': True,
            'behavioral_flag': ''
        })
        self.assertEqual(AttendanceRecord.objects.filter(student=self.student).count(), 0)
        self.assertContains(response, 'Cannot log attendance for a future date.')

    def test_csv_export_blocked_and_allowed(self):
        # Fills export filter requirement & RBAC check
        self.client.login(username='t1', password='pw') # Teacher
        response = self.client.get(reverse('export_cases_csv'))
        self.assertEqual(response.status_code, 302) # Blocked
        
        self.client.login(username='c1', password='pw') # Counselor
        response = self.client.get(reverse('export_cases_csv'))
        self.assertEqual(response.status_code, 200) # Allowed
        self.assertEqual(response['Content-Type'], 'text/csv') 
