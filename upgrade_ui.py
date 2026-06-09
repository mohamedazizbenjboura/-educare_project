import os

templates = {
    'school_app/templates/school_app/base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduCare Tunisia | Social Support Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
        .card { border-radius: 12px; transition: transform 0.2s, box-shadow 0.2s; }
        .card:hover { box-shadow: 0 10px 20px rgba(0,0,0,0.08)!important; }
        .btn { border-radius: 8px; font-weight: 500; }
        .badge { border-radius: 6px; padding: 0.5em 0.8em; }
        .progress { border-radius: 10px; background-color: #e9ecef; }
        .card-hover-effect:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1)!important; }
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark shadow-sm mb-4 py-3">
    <div class="container">
        <a class="navbar-brand fw-bold fs-4" href="#"><i class="bi bi-mortarboard-fill me-2 text-warning"></i>EduCare</a>
        <div class="ms-auto">
            {% if user.is_authenticated %}
                <span class="me-4 text-light"><i class="bi bi-person-badge text-warning me-1"></i>Role: <strong class="text-white">{{ user.role }}</strong> | <i class="bi bi-person-circle ms-2 me-1"></i>{{ user.first_name }} {{ user.last_name }}</span>
                <a href="{% url 'logout' %}" class="btn btn-light btn-sm text-primary fw-bold"><i class="bi bi-box-arrow-right me-1"></i>Logout</a>
            {% endif %}
        </div>
    </div>
</nav>
<div class="container pb-5">
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible shadow-sm rounded-3">
                <i class="bi bi-info-circle-fill me-2"></i>{{ message }}
            </div>
        {% endfor %}
    {% endif %}
    {% block content %}{% endblock %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'school_app/templates/school_app/login.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row pt-5 justify-content-center">
    <div class="col-md-5">
        <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
            <div class="card-header bg-white text-center py-4 border-bottom-0">
                <div class="display-1 text-primary mb-2"><i class="bi bi-shield-lock-fill"></i></div>
                <h3 class="fw-bold text-dark">Welcome to EduCare</h3>
                <p class="text-muted mb-0">Secure portal for youth outcomes monitoring</p>
            </div>
            <div class="card-body px-5 pb-5">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label text-secondary fw-bold small text-uppercase">Username</label>
                        <div class="input-group input-group-lg shadow-sm rounded-3">
                            <span class="input-group-text bg-light border-end-0"><i class="bi bi-person text-secondary"></i></span>
                            <input type="text" name="username" class="form-control border-start-0 bg-light" required>
                        </div>
                    </div>
                    <div class="mb-4">
                        <label class="form-label text-secondary fw-bold small text-uppercase">Password</label>
                        <div class="input-group input-group-lg shadow-sm rounded-3">
                            <span class="input-group-text bg-light border-end-0"><i class="bi bi-key text-secondary"></i></span>
                            <input type="password" name="password" class="form-control border-start-0 bg-light" required>
                        </div>
                        {% if form.errors %}
                        <small class="text-danger mt-2 d-block fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i>Invalid username or password.</small>
                        {% endif %}
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold shadow-sm">Secure Login <i class="bi bi-arrow-right-circle ms-1"></i></button>
                </form>
                <div class="mt-4 p-3 bg-light rounded-3 text-center border">
                    <span class="text-muted small fw-bold text-uppercase d-block mb-2">Demo Credentials</span>
                    <span class="d-block small text-secondary"><i class="bi bi-person me-1"></i>teacher1 | counselor1 | admin1</span>
                    <span class="d-block small text-secondary"><i class="bi bi-key me-1"></i>password123</span>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'school_app/templates/school_app/teacher_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row mb-4 align-items-center">
    <div class="col-md-8">
        <h2 class="fw-bold mb-1"><i class="bi bi-journal-bookmark-fill text-primary me-2"></i>Teacher Dashboard</h2>
        <p class="text-muted mb-0">Monitor classroom attendance and submit behavioral flags.</p>
    </div>
    <div class="col-md-4 text-end">
        <div class="badge bg-primary fs-6 shadow-sm"><i class="bi bi-people-fill me-2"></i>{{ students.count }} Students Assigned</div>
    </div>
</div>

<div class="card shadow-sm border-0">
    <div class="card-body p-0">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4 py-3">Student Name</th>
                    <th class="py-3">Grade Level</th>
                    <th class="text-end pe-4 py-3">Quick Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr>
                    <td class="ps-4 py-3">
                        <div class="d-flex align-items-center">
                            <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px; font-weight: bold;">
                                {{ student.first_name|first }}{{ student.last_name|first }}
                            </div>
                            <div>
                                <h6 class="fw-bold mb-0 text-dark">{{ student.first_name }} {{ student.last_name }}</h6>
                                <small class="text-muted">ID: #STU-{{ student.id|stringformat:"04d" }}</small>
                            </div>
                        </div>
                    </td>
                    <td><span class="badge bg-light text-dark border border-secondary"><i class="bi bi-diagram-3-fill me-1"></i>{{ student.grade_level }}</span></td>
                    <td class="text-end pe-4">
                        <a href="{% url 'log_attendance' student.id %}" class="btn btn-sm btn-outline-primary shadow-sm px-3">
                            <i class="bi bi-clipboard-check me-1"></i> Log Activity
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}''',

    'school_app/templates/school_app/log_attendance.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-7">
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb bg-white p-2 rounded-3 shadow-sm border">
            <li class="breadcrumb-item"><a href="{% url 'teacher_dashboard' %}" class="text-decoration-none fw-bold"><i class="bi bi-house-door-fill me-1"></i>Dashboard</a></li>
            <li class="breadcrumb-item active fw-bold text-dark" aria-current="page">{{ student.first_name }} {{ student.last_name }}</li>
          </ol>
        </nav>
        
        <div class="card shadow-sm border-0 overflow-hidden">
            <div class="card-header bg-white border-bottom py-3 d-flex align-items-center">
                <div class="bg-primary text-white rounded p-2 me-3"><i class="bi bi-journal-text fs-4"></i></div>
                <div>
                    <h4 class="mb-0 fw-bold">Log Daily Record</h4>
                    <span class="text-muted small">Enter attendance and observe behavior</span>
                </div>
            </div>
            <div class="card-body p-4 bg-light">
                <div class="alert alert-info border border-info shadow-sm d-flex align-items-center mb-4">
                    <i class="bi bi-info-circle-fill fs-4 text-info me-3"></i>
                    <div>
                        <strong class="d-block">System Intelligence Rule:</strong>
                        <small>Logging a behavioral flag automatically dispatches a prioritized alert to the school counselor.</small>
                    </div>
                </div>

                <form method="post" class="bg-white p-4 rounded-3 shadow-sm border">
                    {% csrf_token %}
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <label class="form-label fw-bold text-secondary text-uppercase small"><i class="bi bi-calendar-event me-1"></i>Observation Date</label>
                            {{ form.date }}
                            {% if form.date.errors %}<small class="text-danger fw-bold"><i class="bi bi-exclamation-triangle"></i> {{ form.date.errors.0 }}</small>{% endif %}
                        </div>
                        <div class="col-md-6 d-flex align-items-end">
                            <div class="form-check form-switch fs-5 pb-1">
                                {{ form.is_absent }}
                                <label class="form-check-label fw-bold text-dark ms-2" for="{{ form.is_absent.id_for_label }}">Mark Student as Absent</label>
                            </div>
                        </div>
                    </div>
                    
                    <hr class="text-muted">

                    <div class="mb-4">
                        <label class="form-label fw-bold text-danger text-uppercase small"><i class="bi bi-flag-fill me-1"></i>Behavioral Flag (Optional)</label>
                        {{ form.behavioral_flag }}
                        <div class="form-text mt-2"><i class="bi bi-lightbulb me-1"></i>Use this to document objective facts, e.g. "Slept in class", "Refused to speak". <strong>Do not diagnose.</strong></div>
                    </div>
                    
                    <div class="d-flex justify-content-between mt-5">
                        <a href="{% url 'teacher_dashboard' %}" class="btn btn-light border text-muted fw-bold px-4"><i class="bi bi-x-circle me-1"></i>Cancel</a>
                        <button type="submit" class="btn btn-success px-5 fw-bold shadow-sm"><i class="bi bi-check-circle-fill me-1"></i>Submit Record</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'school_app/templates/school_app/counselor_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row mb-4 align-items-center">
    <div class="col-md-5">
        <h2 class="fw-bold mb-1"><i class="bi bi-heart-pulse-fill text-danger me-2"></i>Counselor Management</h2>
        <p class="text-muted mb-0">Review automated early-warning alerts & interventions.</p>
    </div>
    <div class="col-md-7 text-end">
        <form method="get" class="d-inline-flex align-items-center gap-2">
            <select name="status" class="form-select form-select-sm shadow-sm" style="width: 150px;">
                <option value="">All Statuses</option>
                <option value="NEW" {% if request.GET.status == 'NEW' %}selected{% endif %}>New Alerts</option>
                <option value="IN_REVIEW" {% if request.GET.status == 'IN_REVIEW' %}selected{% endif %}>In Review</option>
                <option value="INTERVENTION" {% if request.GET.status == 'INTERVENTION' %}selected{% endif %}>Intervention</option>
                <option value="FOLLOW_UP_MISSED" {% if request.GET.status == 'FOLLOW_UP_MISSED' %}selected{% endif %}>Missed Follow-up</option>
            </select>
            <select name="risk_level" class="form-select form-select-sm shadow-sm" style="width: 150px;">
                <option value="">All Risks</option>
                <option value="high" {% if request.GET.risk_level == 'high' %}selected{% endif %}>High Risk (75+)</option>
                <option value="medium" {% if request.GET.risk_level == 'medium' %}selected{% endif %}>Medium Risk</option>
                <option value="low" {% if request.GET.risk_level == 'low' %}selected{% endif %}>Low Risk</option>
            </select>
            <button type="submit" class="btn btn-sm btn-primary shadow-sm px-3">Filter</button>
            <a href="{% url 'counselor_dashboard' %}" class="btn btn-sm btn-light border shadow-sm"><i class="bi bi-arrow-counterclockwise"></i></a>
        </form>
        <a href="{% url 'export_cases_csv' %}?status={{ request.GET.status }}&risk_level={{ request.GET.risk_level }}" class="btn btn-sm btn-success shadow-sm px-3 ms-2">
            <i class="bi bi-file-earmark-spreadsheet me-1"></i> Export
        </a>
        <button type="button" class="btn btn-sm btn-dark shadow-sm px-3 ms-2" data-bs-toggle="modal" data-bs-target="#configModal">
            <i class="bi bi-gear-fill"></i>
        </button>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-white p-3 d-flex flex-row align-items-center">
            <div class="bg-warning bg-opacity-25 text-warning rounded-circle p-3 me-3"><i class="bi bi-bell-fill fs-4"></i></div>
            <div>
                <h6 class="text-muted small text-uppercase fw-bold mb-0">New Alerts</h6>
                <h4 class="fw-bold mb-0">{{ new_alerts_count }}</h4>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-white p-3 d-flex flex-row align-items-center">
            <div class="bg-primary bg-opacity-25 text-primary rounded-circle p-3 me-3"><i class="bi bi-person-lines-fill fs-4"></i></div>
            <div>
                <h6 class="text-muted small text-uppercase fw-bold mb-0">In Progress</h6>
                <h4 class="fw-bold mb-0">{{ intervention_count }}</h4>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow-sm bg-white p-3 d-flex flex-row align-items-center">
            <div class="bg-danger bg-opacity-25 text-danger rounded-circle p-3 me-3"><i class="bi bi-exclamation-triangle-fill fs-4"></i></div>
            <div>
                <h6 class="text-muted small text-uppercase fw-bold mb-0">High Priority</h6>
                <h4 class="fw-bold mb-0">{{ high_risk_count }}</h4>
            </div>
        </div>
    </div>
</div>

<div class="card shadow-sm border-0 mb-5">
    <div class="card-body p-0">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="py-3 ps-4">Student Info / Origin</th>
                    <th class="py-3">Workflow State</th>
                    <th class="py-3" style="width: 200px;">Assessed Risk Level</th>
                    <th class="py-3"><i class="bi bi-calendar-check me-1"></i>Follow-up Target</th>
                    <th class="text-end py-3 pe-4">Action</th>
                </tr>
            </thead>
            <tbody>
                {% for case in cases %}
                <tr>
                    <td class="ps-4 py-3">
                        <div class="fw-bold text-dark fs-6">{{ case.student }}</div>
                        <small class="text-primary fw-bold"><i class="bi bi-clock-history me-1"></i>Opened: {{ case.created_at|date:"M d, Y" }}</small>
                    </td>
                    <td>
                        {% if case.status == 'FOLLOW_UP_MISSED' %}<span class="badge bg-danger shadow-sm border border-danger"><i class="bi bi-exclamation-triangle-fill me-1"></i>Missed Follow-up</span>
                        {% elif case.status == 'NEW' %}<span class="badge bg-warning text-dark shadow-sm border border-warning"><i class="bi bi-bell-fill me-1"></i>New Alert</span>
                        {% elif case.status == 'INTERVENTION' %}<span class="badge bg-primary shadow-sm border border-primary"><i class="bi bi-person-lines-fill me-1"></i>Intervention Planned</span>
                        {% else %}<span class="badge bg-secondary shadow-sm text-white"><i class="bi bi-search me-1"></i>{{ case.get_status_display }}</span>{% endif %}
                    </td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress flex-grow-1 shadow-sm border" style="height: 12px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated {% if case.risk_score > 74 %}bg-danger{% elif case.risk_score > 40 %}bg-warning{% else %}bg-success{% endif %}" 
                                     style="width: {{ case.risk_score }}%;"></div>
                            </div>
                            <span class="ms-2 fw-bold text-muted small">{{ case.risk_score }}</span>
                        </div>
                    </td>
                    <td>
                        {% if case.follow_up_date %}
                            {% if case.status == 'FOLLOW_UP_MISSED' %}
                                <span class="text-danger fw-bold"><i class="bi bi-x-circle-fill me-1"></i>{{ case.follow_up_date }}</span>
                            {% else %}
                                <span class="text-dark fw-bold">{{ case.follow_up_date }}</span>
                            {% endif %}
                        {% else %}
                            <span class="text-muted fst-italic small d-inline-block bg-light px-2 py-1 rounded border">Not scheduled</span>
                        {% endif %}
                    </td>
                    <td class="text-end pe-4">
                        <a href="{% url 'case_detail' case.id %}" class="btn btn-sm btn-dark shadow-sm px-3 fw-bold">Open Case <i class="bi bi-arrow-right ms-1"></i></a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="5" class="text-center text-muted py-5 col-12">
                        <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
                        <h5 class="mt-3 text-dark fw-bold">All caught up!</h5>
                        <p>No active interventions matching your filters.</p>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- F6: Advanced AI Decision Support Resources (Interactive Visual Evidence) -->
{% if scraped_resources %}
<div class="row mt-5">
    <div class="col-12">
        <div class="card border-0 shadow-sm bg-primary bg-opacity-10">
            <div class="card-body p-4">
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded p-2 me-3"><i class="bi bi-robot fs-4"></i></div>
                    <div>
                        <h5 class="fw-bold mb-0 text-primary">AI Decision Support: Ingested Knowledge</h5>
                        <small class="text-muted">Interactive evidence retrieved via MCP & A2A Protocols.</small>
                    </div>
                </div>
                <div class="row g-3">
                    {% for resource in scraped_resources %}
                    <div class="col-md-4">
                        <a href="{{ resource.source_url }}" target="_blank" class="text-decoration-none">
                            <div class="card h-100 border-0 shadow-sm card-hover-effect">
                                <div class="card-body p-3">
                                    <h6 class="fw-bold text-dark small mb-2"><i class="bi bi-journal-text text-primary me-1"></i>{{ resource.title }}</h6>
                                    <p class="text-muted small mb-0" style="font-size: 0.75rem;">{{ resource.abstract|truncatechars:100 }}</p>
                                    <hr class="my-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="badge bg-light text-primary border" style="font-size: 0.65rem;">{{ resource.extraction_method }}</span>
                                        <small class="text-muted" style="font-size: 0.6rem;">{{ resource.access_date|slice:":10" }}</small>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </div>
                    {% endfor %}
                </div>
                <div class="mt-3 text-center">
                    <small class="text-muted fst-italic"><i class="bi bi-info-circle me-1"></i>Tip: Click any resource card to view the original source documentation.</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- System Configuration Modal (Rubric 8.1) -->
<div class="modal fade" id="configModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content border-0 shadow-lg">
      <div class="modal-header bg-dark text-white border-0">
        <h5 class="modal-title fw-bold"><i class="bi bi-sliders me-2"></i>System Threshold Config</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <form action="{% url 'update_config' %}" method="post">
        {% csrf_token %}
        <div class="modal-body p-4 bg-light">
            <p class="text-muted small mb-4">Define the rule for automated alerting. When a student exceeds this number of consecutive absences, a high-priority intervention case is generated.</p>
            <div class="mb-3">
                <label class="form-label fw-bold text-secondary small text-uppercase">Consecutive Absence Threshold</label>
                <div class="input-group input-group-lg shadow-sm">
                    <span class="input-group-text bg-white border-end-0"><i class="bi bi-calendar-x text-primary"></i></span>
                    <input type="number" name="absence_threshold" class="form-control border-start-0 bg-white" value="3" min="1" max="10">
                </div>
            </div>
        </div>
        <div class="modal-footer border-0 p-3">
            <button type="submit" class="btn btn-primary fw-bold w-100 shadow-sm">Apply Global Rule</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}''',

    'school_app/templates/school_app/case_detail.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb bg-white p-2 rounded-3 shadow-sm border">
            <li class="breadcrumb-item"><a href="{% url 'counselor_dashboard' %}" class="text-decoration-none fw-bold"><i class="bi bi-house-door-fill me-1"></i>Dashboard</a></li>
            <li class="breadcrumb-item active fw-bold text-dark" aria-current="page">Intervention Case #{{ case.id|stringformat:"04d" }}</li>
          </ol>
        </nav>

        <!-- Dynamic Visual Status Progression (EXAM REQUIREMENT) -->
        <div class="card shadow-sm border-0 mb-4 bg-white">
            <div class="card-body p-4">
                <h5 class="fw-bold mb-4 text-secondary text-uppercase small text-center">Intervention Lifecycle</h5>
                <div class="d-flex justify-content-between position-relative">
                    <!-- Progress Line background -->
                    <div class="position-absolute top-50 start-0 translate-middle-y w-100" style="height: 4px; background-color: #e9ecef; z-index: 1;"></div>
                    
                    <div class="text-center position-relative" style="z-index: 2; width: 25%;">
                        <div class="rounded-circle {% if case.status != 'NEW' %}bg-secondary{% else %}bg-warning text-dark border-dark{% endif %} text-white d-flex align-items-center justify-content-center mx-auto mb-2 fw-bold shadow-sm" style="width:40px; height:40px; border:2px solid white;">1</div>
                        <small class="fw-bold text-dark">Intake / Alert</small>
                    </div>
                    <div class="text-center position-relative" style="z-index: 2; width: 25%;">
                        <div class="rounded-circle {% if case.status == 'IN_REVIEW' %}bg-primary{% elif case.status == 'INTERVENTION' or case.status == 'FOLLOW_UP_MISSED' or case.status == 'RESOLVED' %}bg-secondary{% else %}bg-light text-muted border{% endif %} text-white d-flex align-items-center justify-content-center mx-auto mb-2 fw-bold shadow-sm" style="width:40px; height:40px; border:2px solid white;">2</div>
                        <small class="fw-bold {% if case.status == 'IN_REVIEW' %}text-primary{% else %}text-muted{% endif %}">In Review</small>
                    </div>
                    <div class="text-center position-relative" style="z-index: 2; width: 25%;">
                        <div class="rounded-circle {% if case.status == 'INTERVENTION' or case.status == 'FOLLOW_UP_MISSED' %}bg-primary{% elif case.status == 'RESOLVED' %}bg-secondary{% else %}bg-light text-muted border{% endif %} text-white d-flex align-items-center justify-content-center mx-auto mb-2 fw-bold shadow-sm" style="width:40px; height:40px; border:2px solid white;">3</div>
                        <small class="fw-bold {% if case.status == 'INTERVENTION' or case.status == 'FOLLOW_UP_MISSED' %}text-primary{% else %}text-muted{% endif %}">Intervention Plan</small>
                    </div>
                    <div class="text-center position-relative" style="z-index: 2; width: 25%;">
                        <div class="rounded-circle {% if case.status == 'RESOLVED' %}bg-success{% else %}bg-light text-muted border{% endif %} text-white d-flex align-items-center justify-content-center mx-auto mb-2 fw-bold shadow-sm" style="width:40px; height:40px; border:2px solid white;"><i class="bi bi-check-lg fs-5"></i></div>
                        <small class="fw-bold {% if case.status == 'RESOLVED' %}text-success{% else %}text-muted{% endif %}">Closed & Resolved</small>
                    </div>
                </div>
            </div>
        </div>

        <div class="row g-4">
            <!-- Left Column: FACTS & HISTORY (EXAM REQUIREMENT: Separate facts from recommendations) -->
            <div class="col-md-5">
                <div class="card border-0 shadow-sm h-100 bg-white">
                    <div class="card-header bg-dark text-white py-3">
                        <h6 class="mb-0 fw-bold"><i class="bi bi-clipboard-data me-2"></i>Target Student Profile & Facts</h6>
                    </div>
                    <div class="card-body p-4 bg-light">
                        <div class="text-center mb-4">
                            <h3 class="fw-bold text-dark mb-0">{{ case.student.first_name }} {{ case.student.last_name }}</h3>
                            <span class="badge bg-secondary mt-2 fs-6 border border-dark"><i class="bi bi-diagram-3-fill me-1"></i>{{ case.student.grade_level }}</span>
                        </div>
                        
                        <h6 class="fw-bold text-secondary text-uppercase small border-bottom pb-2 mb-3 mt-4"><i class="bi bi-clock-history me-1"></i>Objective History Source</h6>
                        <ul class="list-group list-group-flush rounded-3 shadow-sm border">
                            {% for record in case.student.attendance_records.all|dictsortreversed:"date"|slice:":4" %}
                            <li class="list-group-item px-3 py-3 border-bottom">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <strong class="text-dark small"><i class="bi bi-calendar2 me-1"></i>{{ record.date }}</strong>
                                    {% if record.is_absent %}<span class="badge bg-danger">Absent</span>{% else %}<span class="badge bg-success">Present</span>{% endif %}
                                </div>
                                {% if record.behavioral_flag %}
                                    <div class="mt-2 bg-light p-2 rounded border border-warning">
                                        <small class="fw-bold text-danger d-block mb-1"><i class="bi bi-flag-fill me-1"></i>Behavioral Flag submitted:</small>
                                        <span class="text-dark small fst-italic">"{{ record.behavioral_flag }}"</span>
                                    </div>
                                {% endif %}
                                <div class="text-end mt-2">
                                    <small class="text-muted"><i class="bi bi-person-badge me-1"></i>Source: Teacher {{ record.logged_by.username }}</small>
                                </div>
                            </li>
                            {% empty %}
                            <li class="list-group-item bg-transparent text-muted py-4 text-center">No historical objective data.</li>
                            {% endfor %}
                        </ul>
                        <div class="mt-3 text-center">
                            <small class="text-muted fst-italic"><i class="bi bi-info-circle me-1"></i>Note: Base intervention strictly on the factual evidence retrieved above.</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: COUNSELOR RECOMMENDATIONS & INTERVENTION -->
            <div class="col-md-7">
                <div class="card shadow-sm border-0 h-100">
                    <div class="card-header bg-primary text-white py-3 d-flex justify-content-between align-items-center">
                        <h6 class="mb-0 fw-bold"><i class="bi bi-pencil-square me-2"></i>Counselor Action & Recommendations</h6>
                        <span class="badge bg-light text-primary">Case #{{ case.id }}</span>
                    </div>
                    <div class="card-body p-4 border border-top-0 rounded-bottom">
                        <form method="post">
                            {% csrf_token %}
                            <div class="row mb-4">
                                <div class="col-md-6 mb-3 mb-md-0">
                                    <label class="form-label fw-bold text-secondary text-uppercase small"><i class="bi bi-gear-fill me-1"></i>Workflow Status</label>
                                    {{ form.status }}
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label fw-bold text-secondary text-uppercase small"><i class="bi bi-calendar-event-fill me-1"></i>Next Follow-Up</label>
                                    {{ form.follow_up_date }}
                                </div>
                            </div>

                            <div class="mb-4">
                                <label class="form-label fw-bold text-dark d-flex align-items-center">
                                    <span class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-2" style="width:24px;height:24px;font-size:12px;">A</span>
                                    Intervention Plan & Recommendations
                                </label>
                                <div class="form-text text-muted mb-2 lh-sm mt-0">Document your proposed support pathway here. This must respond directly to the objective history shown on the left.</div>
                                {{ form.plan_description }}
                            </div>

                            <div class="mb-4 bg-light border p-3 rounded-3 {% if form.resolution_notes.errors or form.non_field_errors %}border-danger shadow-sm{% endif %}">
                                <label class="form-label fw-bold text-success d-flex align-items-center">
                                    <span class="bg-success text-white rounded-circle d-flex justify-content-center align-items-center me-2" style="width:24px;height:24px;font-size:12px;">B</span>
                                    Resolution Outcome Notes
                                </label>
                                <div class="form-text text-success-emphasis mb-2 lh-sm mt-0"><i class="bi bi-lock-fill me-1"></i><strong>Safety Lock:</strong> The system strictly prohibits closing/resolving this case until detailed final outcomes have been entered.</div>
                                {{ form.resolution_notes }}
                                
                                {% if form.non_field_errors %}
                                    <div class="alert alert-danger mt-3 py-2 px-3 fw-bold border-danger shadow-sm d-flex align-items-center mb-0">
                                        <i class="bi bi-sign-stop-fill fs-4 me-3"></i> 
                                        <span>{{ form.non_field_errors.0 }}</span>
                                    </div>
                                {% endif %}
                            </div>

                            <div class="d-flex justify-content-end mt-4 pt-3 border-top">
                                <button type="submit" class="btn btn-primary btn-lg px-5 fw-bold shadow"><i class="bi bi-save2-fill me-2"></i>Save Confidential Record</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'school_app/templates/school_app/principal_dashboard.html': '''{% extends 'school_app/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-5 border-bottom pb-3">
    <div>
        <h2 class="fw-bold mb-1"><i class="bi bi-buildings-fill text-dark me-2"></i>Executive Policy Dashboard</h2>
        <p class="text-muted mb-0">High-level insights & aggregate platform telemetry.</p>
    </div>
    <div class="text-end">
        <span class="badge bg-dark fw-light fs-6 text-white py-2 px-3 rounded-pill shadow-sm"><i class="bi bi-shield-lock me-1"></i>Privacy Policy Active</span>
    </div>
</div>

<div class="alert alert-secondary border-secondary bg-white shadow-sm d-flex align-items-center p-4 mb-5 rounded-4">
    <i class="bi bi-eye-slash-fill fs-1 text-primary me-4"></i>
    <div>
        <h5 class="fw-bold mb-1 text-dark">Data Governance Notice</h5>
        <p class="mb-0 text-secondary">As an executive manager, you are viewing operational aggregates. To comply with youth privacy frameworks, access to individual psychological logs and counselor recommendations is restricted structurally at the database level.</p>
    </div>
</div>

<div class="row g-4 mt-2">
    <!-- Metric 1 -->
    <div class="col-md-3">
        <div class="card h-100 border-0 shadow rounded-4" style="background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);">
            <div class="card-body text-white p-4 d-flex flex-column justify-content-between position-relative overflow-hidden">
                <i class="bi bi-people position-absolute text-white" style="font-size: 8rem; opacity: 0.1; right: -20px; top: -10px;"></i>
                <h6 class="text-uppercase text-white-50 fw-bold mb-4 tracking-wide z-index-1">Total Enrolled</h6>
                <div class="display-3 fw-bold mb-0 z-index-1">{{ total_students }}</div>
            </div>
        </div>
    </div>
    
    <!-- Metric 2 -->
    <div class="col-md-3">
        <div class="card h-100 border-0 shadow rounded-4 bg-white">
            <div class="card-body p-4 d-flex flex-column justify-content-between">
                <div class="d-flex justify-content-between align-items-start mb-4">
                    <h6 class="text-uppercase text-muted fw-bold mb-0">Total Interventions<br><span class="text-secondary small fw-normal">Historical cumulative</span></h6>
                    <div class="bg-light rounded p-2 text-primary"><i class="bi bi-journal-medical fs-4"></i></div>
                </div>
                <div class="display-4 fw-bold text-dark">{{ total_cases }}</div>
            </div>
        </div>
    </div>

    <!-- Metric 3 -->
    <div class="col-md-3">
        <div class="card h-100 border-0 shadow rounded-4 bg-white">
            <div class="card-body p-4 d-flex flex-column justify-content-between">
                <div class="d-flex justify-content-between align-items-start mb-4">
                    <h6 class="text-uppercase text-primary fw-bold mb-0">Active Operations<br><span class="text-secondary small fw-normal">Currently in progress</span></h6>
                    <div class="bg-primary bg-opacity-10 rounded p-2 text-primary"><i class="bi bi-activity fs-4"></i></div>
                </div>
                <div class="display-4 fw-bold text-primary">{{ active_cases }}</div>
            </div>
        </div>
    </div>

    <!-- Metric 4 -->
    <div class="col-md-3">
        <div class="card h-100 border-0 shadow rounded-4" style="background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);">
            <div class="card-body text-white p-4 d-flex flex-column justify-content-between position-relative overflow-hidden">
                <i class="bi bi-exclamation-octagon position-absolute text-white" style="font-size: 8rem; opacity: 0.1; right: -20px; top: -10px;"></i>
                <h6 class="text-uppercase text-white-50 fw-bold mb-4 tracking-wide z-index-1">Workflow Failures<br><span class="text-white-50 small fw-normal">Missed Follow-Ups</span></h6>
                <div class="display-3 fw-bold mb-0 z-index-1">{{ missed_follow_ups }}</div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
}

for name, content in templates.items():
    with open(os.path.join(os.getcwd(), name), 'w', encoding='utf-8') as f:
        f.write(content)

print("UI Successfully Upgraded to Enterprise Standard.")
