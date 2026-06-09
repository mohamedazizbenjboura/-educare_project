# Roles and Matrix Configurations

The platform utilizes a strictly enforced Role-Based Access Control (RBAC) model implemented using Django's `@user_passes_test` and specialized validation methodologies.

| Action / Capability | Teacher (Operator) | Counselor (Supervisor) | Principal (Manager) |
| :--- | :--- | :--- | :--- |
| **Log Attendance** (Create) | ✅ Yes (Only their assigned students) | ❌ No | ❌ No |
| **Submit Behavioral Flag** (Create) | ✅ Yes | ❌ No | ❌ No |
| **Review Automated Alerts** (Read) | ❌ No | ✅ Yes (All active alerts) | ❌ No (Can only see statistical aggregates) |
| **Formulate Intervention Plan** (Review/Update) | ❌ No | ✅ Yes | ❌ No |
| **Set Follow-up Targets** (Update) | ❌ No | ✅ Yes | ❌ No |
| **Resolve & Close Case** (Validate) | ❌ No | ✅ Yes (requires mandatory text inputs) | ❌ No |
| **View Executive Metrics & KPIs** (Read)| ❌ No | ❌ No | ✅ Yes (School-wide aggregates only) |

## Key Privacy and Access Controls
- **Teachers** are physically bound to standard operations (`assigned_teacher` mapping constraint in `Student` model filters).
- **Counselor Notes** are heavily shielded. Neither Teachers nor Principals have the capability to query the `resolution_notes` or `plan_description` texts.
- **Fail-safe Injection Recovery:** Unauthorized navigations (e.g. Teacher manually trying to URL hack into `/counselor/case/1`) are handled securely and redirected automatically without crashing the system or leaking metadata boundaries.