import os

files = {
    'educare_project/settings.py': lambda content: content + "\nLOGIN_URL = 'login'\n",
    'educare_project/urls.py': '''from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/')),
    path('', include('school_app.urls')),
]
''',
    'school_app/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/attendance/<int:student_id>/', views.log_attendance, name='log_attendance'),
    path('counselor/', views.counselor_dashboard, name='counselor_dashboard'),
    path('counselor/case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('principal/', views.principal_dashboard, name='principal_dashboard'),
]
''',
    'school_app/forms.py': '''from django import forms
from .models import AttendanceRecord, InterventionCase
from django.utils import timezone

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['date', 'is_absent', 'behavioral_flag']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_absent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'behavioral_flag': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("Cannot log attendance for a future date.")
        return date

class InterventionForm(forms.ModelForm):
    class Meta:
        model = InterventionCase
        fields = ['status', 'plan_description', 'follow_up_date', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'plan_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
''',
    'school_app/views.py': '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from .models import Student, AttendanceRecord, InterventionCase
from .forms import AttendanceForm, InterventionForm
from django.core.exceptions import ValidationError

def is_teacher(user): return user.role == 'TEACHER'
def is_counselor(user): return user.role == 'COUNSELOR'
def is_principal(user): return user.role == 'PRINCIPAL'

def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'TEACHER': return redirect('teacher_dashboard')
        elif request.user.role == 'COUNSELOR': return redirect('counselor_dashboard')
        elif request.user.role == 'PRINCIPAL': return redirect('principal_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'TEACHER': return redirect('teacher_dashboard')
            elif user.role == 'COUNSELOR': return redirect('counselor_dashboard')
            elif user.role == 'PRINCIPAL': return redirect('principal_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'school_app/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    students = Student.objects.filter(assigned_teacher=request.user)
    return render(request, 'school_app/teacher_dashboard.html', {'students': students})

@login_required
@user_passes_test(is_teacher)
def log_attendance(request, student_id):
    student = get_object_or_404(Student, id=student_id, assigned_teacher=request.user)
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.student = student
            record.logged_by = request.user
            try:
                record.save()
                messages.success(request, f"Attendance logged for {student}.")
                
                # Scenario 1 Logic: Trigger Alert if flag is present
                if record.behavioral_flag:
                    InterventionCase.objects.create(
                        student=student, 
                        status='NEW', 
                        risk_score=75,
                        plan_description=f"Automated alert: Behavioral flag logged by {request.user.username}: {record.behavioral_flag}"
                    )
                    messages.warning(request, "A behavioral flag automatically alerted the counselor.")
                elif record.is_absent:
                    # Check if 3 consecutive absences
                    recent_absences = AttendanceRecord.objects.filter(student=student).order_by('-date')[:3]
                    if len(recent_absences) == 3 and all(r.is_absent for r in recent_absences):
                         InterventionCase.objects.get_or_create(
                            student=student, 
                            status='NEW',
                            defaults={'risk_score': 80, 'plan_description':"Automated alert: 3 consecutive absences."}
                        )
                         messages.warning(request, "Consecutive absences automatically alerted the counselor.")
                return redirect('teacher_dashboard')
            except Exception as e:
                messages.error(request, f"Error: Cannot log duplicate entry for {record.date}")
    else:
        form = AttendanceForm(initial={'date': timezone.now().date()})
    return render(request, 'school_app/log_attendance.html', {'form': form, 'student': student})

@login_required
@user_passes_test(is_counselor)
def counselor_dashboard(request):
    # Scenario 2 Logic: Check for missed follow-ups
    today = timezone.now().date()
    missed = InterventionCase.objects.filter(status='INTERVENTION', follow_up_date__lt=today)
    missed.update(status='FOLLOW_UP_MISSED')
    
    cases = InterventionCase.objects.exclude(status='RESOLVED').order_by('-risk_score', 'created_at')
    return render(request, 'school_app/counselor_dashboard.html', {'cases': cases})

@login_required
@user_passes_test(is_counselor)
def case_detail(request, case_id):
    case = get_object_or_404(InterventionCase, id=case_id)
    if request.method == 'POST':
        form = InterventionForm(request.POST, instance=case)
        if form.is_valid():
            try:
                c = form.save(commit=False)
                c.counselor = request.user
                c.clean() # Model-level validation enforcement!
                c.save()
                messages.success(request, "Case updated successfully.")
                return redirect('counselor_dashboard')
            except ValidationError as e:
                messages.error(request, f"Validation Error: {e.messages[0]}")
    else:
        form = InterventionForm(instance=case)
    return render(request, 'school_app/case_detail.html', {'form': form, 'case': case})

@login_required
@user_passes_test(is_principal)
def principal_dashboard(request):
    Total_students = Student.objects.count()
    total_cases = InterventionCase.objects.count()
    active_cases = InterventionCase.objects.exclude(status='RESOLVED').count()
    missed_follow_ups = InterventionCase.objects.filter(status='FOLLOW_UP_MISSED').count()
    
    return render(request, 'school_app/principal_dashboard.html', {
        'total_students': Total_students,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'missed_follow_ups': missed_follow_ups
    })
''',
    'school_app/tests.py': '''from django.test import TestCase, Client
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
        self.assertContains(response, 'Validation Error: Resolution notes are required when closing a case.') 
'''
}

import os

for path, content in files.items():
    if callable(content):
        with open(path, 'r', encoding='utf-8') as f:
            old = f.read()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content(old))
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# Templates
os.makedirs('school_app/templates/school_app', exist_ok=True)
templates = {
    'base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EduCare Tunisia | Social Support Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm mb-4">
    <div class="container">
        <a class="navbar-brand text-light fw-bold" href="#">🎓 EduCare</a>
        <div class="ms-auto">
            {% if user.is_authenticated %}
                <span class="me-3 text-light">Role: <strong class="badge bg-secondary">{{ user.role }}</strong> | 👤 {{ user.first_name }} {{ user.last_name }}</span>
                <a href="{% url 'logout' %}" class="btn btn-outline-light btn-sm">Logout</a>
            {% endif %}
        </div>
    </div>
</nav>
<div class="container pb-5">
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible shadow-sm">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    {% block content %}{% endblock %}
</div>
</body>
</html>''',

    'login.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row pt-5 justify-content-center">
    <div class="col-md-5">
        <div class="card shadow-lg border-0 rounded-3">
            <div class="card-header bg-primary text-white text-center py-4">
                <h4 class="mb-0">Welcome to EduCare</h4>
            </div>
            <div class="card-body p-4">
                <p class="text-muted text-center mb-4">A platform for monitoring youth outcomes and preventing dropout.</p>
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Password</label>
                        <input type="password" name="password" class="form-control" required>
                        {% if form.errors %}
                        <small class="text-danger mt-1 d-block">Invalid username or password.</small>
                        {% endif %}
                    </div>
                    <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Login</button>
                </form>
                <hr class="mt-4">
                <div class="text-center text-muted small">
                    Demo accounts: teacher1 / counselor1 / admin1<br>Pass: password123
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'teacher_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="fw-bold mb-0">Teacher Dashboard</h2>
    <span class="text-muted">Track attendance & behavior</span>
</div>
<div class="card shadow-sm border-0">
    <div class="card-body">
        <table class="table table-hover align-middle">
            <thead class="table-light"><tr><th>Student Name</th><th>Grade Level</th><th class="text-end">Action</th></tr></thead>
            <tbody>
                {% for student in students %}
                <tr>
                    <td><div class="fw-bold">{{ student.first_name }} {{ student.last_name }}</div></td>
                    <td><span class="badge bg-secondary">{{ student.grade_level }}</span></td>
                    <td class="text-end">
                        <a href="{% url 'log_attendance' student.id %}" class="btn btn-sm btn-outline-primary">Log Activity / Flag</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}''',

    'log_attendance.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{% url 'teacher_dashboard' %}" class="text-decoration-none">Dashboard</a></li>
            <li class="breadcrumb-item active" aria-current="page">{{ student.first_name }} {{ student.last_name }}</li>
          </ol>
        </nav>
        <div class="card shadow-sm border-0">
            <div class="card-body p-4">
                <h4 class="mb-4">Log Daily Record</h4>
                <div class="alert alert-info border-0 shadow-sm py-2 px-3 mb-4">
                    <small>System Rule: If a behavioral flag is submitted, an automatic alert is created for the school counselor.</small>
                </div>
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label fw-bold">Date</label>
                        {{ form.date }}
                        {% if form.date.errors %}<small class="text-danger">{{ form.date.errors }}</small>{% endif %}
                    </div>
                    <div class="mb-3 form-check">
                        {{ form.is_absent }}
                        <label class="form-check-label fw-bold" for="{{ form.is_absent.id_for_label }}">Mark as absent</label>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold text-danger">Optional Behavioral Flag</label>
                        {{ form.behavioral_flag }}
                        <small class="text-muted d-block mt-1">Leave empty unless intervention is required (e.g. "Slept in class").</small>
                    </div>
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'teacher_dashboard' %}" class="btn btn-light border">Cancel</a>
                        <button type="submit" class="btn btn-success px-4">Submit Record</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'counselor_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="fw-bold mb-0">Counselor Case Management</h2>
    <span class="text-muted">Review automated alerts & interventions</span>
</div>
<div class="card shadow-sm border-0">
    <div class="card-body">
        <table class="table table-hover align-middle">
            <thead class="table-light"><tr><th>Student</th><th>Status / Flow</th><th>Risk Score</th><th>Follow-up Target</th><th class="text-end">Review</th></tr></thead>
            <tbody>
                {% for case in cases %}
                <tr>
                    <td><div class="fw-bold">{{ case.student }}</div><small class="text-muted">Created: {{ case.created_at|date:"M d" }}</small></td>
                    <td>
                        {% if case.status == 'FOLLOW_UP_MISSED' %}<span class="badge bg-danger">Missed Follow-up</span>
                        {% elif case.status == 'NEW' %}<span class="badge bg-warning text-dark">New Alert</span>
                        {% elif case.status == 'INTERVENTION' %}<span class="badge bg-primary">Intervention Planned</span>
                        {% else %}<span class="badge bg-secondary">{{ case.get_status_display }}</span>{% endif %}
                    </td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar {% if case.risk_score > 70 %}bg-danger{% else %}bg-warning text-dark{% endif %}" style="width: {{ case.risk_score }}%;">{{ case.risk_score }} / 100</div>
                        </div>
                    </td>
                    <td>{% if case.follow_up_date %}{{ case.follow_up_date }}{% else %}<span class="text-muted fst-italic">Not scheduled</span>{% endif %}</td>
                    <td class="text-end"><a href="{% url 'case_detail' case.id %}" class="btn btn-sm btn-dark">Open Case</a></td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="text-center text-muted py-4">No active interventions at the moment.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}''',

    'case_detail.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-9">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{% url 'counselor_dashboard' %}" class="text-decoration-none">Dashboard</a></li>
            <li class="breadcrumb-item active" aria-current="page">Case #{{ case.id }}</li>
          </ol>
        </nav>
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3 class="mb-0">Student: <span class="text-primary">{{ case.student }}</span></h3>
                    <span class="badge fs-6 {% if case.status == 'NEW' %}bg-warning text-dark{% elif case.status == 'RESOLVED' %}bg-success{% else %}bg-primary{% endif %}">
                        {{ case.get_status_display }}
                    </span>
                </div>
                
                <form method="post">
                    {% csrf_token %}
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-bold">Case Status</label>
                            {{ form.status }}
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-bold">Follow-Up Date</label>
                            {{ form.follow_up_date }}
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Intervention Plan / Incident Notes</label>
                        {{ form.plan_description }}
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold text-success">Resolution Outcome Notes (Required to close)</label>
                        {{ form.resolution_notes }}
                        {% if form.non_field_errors %}
                            <div class="text-danger mt-1 small">{{ form.non_field_errors.0 }}</div>
                        {% endif %}
                    </div>
                    <div class="d-flex justify-content-between">
                        <a href="{% url 'counselor_dashboard' %}" class="btn btn-outline-secondary">Back</a>
                        <button type="submit" class="btn btn-primary px-4 fw-bold">Save Intervention Data</button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="card border-0 shadow-sm bg-light">
            <div class="card-body p-4">
                <h5 class="fw-bold mb-3"><span class="text-muted">History:</span> Recent Attendance</h5>
                <ul class="list-group list-group-flush">
                    {% for record in case.student.attendance_records.all|slice:":5" %}
                    <li class="list-group-item bg-transparent px-0 border-bottom">
                        <strong>{{ record.date }}</strong> — 
                        {% if record.is_absent %}<span class="text-danger me-2">Absent</span>{% else %}<span class="text-success me-2">Present</span>{% endif %}
                        {% if record.behavioral_flag %}
                            <span class="badge border border-danger text-danger bg-white shadow-sm">Flag: {{ record.behavioral_flag }}</span>
                        {% endif %}
                        <small class="text-muted float-end">Logged by {{ record.logged_by.username }}</small>
                    </li>
                    {% empty %}
                    <li class="list-group-item bg-transparent px-0">No records found.</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'principal_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="fw-bold mb-0">Principal Executive Dashboard</h2>
    <span class="text-muted">School-wide metrics and KPIs</span>
</div>
<div class="row mt-4">
    <div class="col-md-3">
        <div class="card border-0 shadow-sm bg-primary text-white text-center p-4">
            <h1 class="display-3 fw-bold">{{ total_students }}</h1><p class="mb-0 text-white-50">Total Enrolled</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm bg-warning text-dark text-center p-4">
            <h1 class="display-3 fw-bold">{{ total_cases }}</h1><p class="mb-0 text-muted">Total Interventions</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm bg-info text-white text-center p-4">
            <h1 class="display-3 fw-bold">{{ active_cases }}</h1><p class="mb-0 text-white-50">Ongoing/Pending Cases</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm bg-danger text-white text-center p-4">
            <h1 class="display-3 fw-bold">{{ missed_follow_ups }}</h1><p class="mb-0 text-white-50">Missed Follow-Ups</p>
        </div>
    </div>
</div>
<div class="row mt-5">
    <div class="col-12 text-center text-muted">
        <p>This read-only dashboard provides overarching insights without revealing confidential counselor notes, maintaining student privacy boundaries.</p>
    </div>
</div>
{% endblock %}'''
}

for name, content in templates.items():
    with open(os.path.join('school_app/templates/school_app', name), 'w', encoding='utf-8') as f:
        f.write(content)
print("Complete Architecture Rebuild Output Successful.")
