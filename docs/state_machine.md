# Application State Machine & Intervention Workflow

The architecture of EduCare strictly adheres to an auditable timeline workflow driven by the `InterventionCase` Django model choices. State transition validation is strictly protected at the code and Database layers.

## Permitted States
1. **`NEW` (Intake / Alert):** Triggered automatically by the system algorithms when a teacher submits a negative behavioral flag OR 3 consecutive absences are recorded.
2. **`IN_REVIEW`:** The counselor is currently evaluating the historical metrics or interviewing the student, but has not yet deployed a mitigation path.
3. **`INTERVENTION`:** An actionable intervention support path is written out and agreed upon, and a `follow_up_date` is successfully injected.
4. **`FOLLOW_UP_MISSED` (Automated System Transition):** The system clock exceeds the `follow_up_date` without resolution or modification. Generates a red-tier warning priority.
5. **`RESOLVED` (Closed):** The issue is concluded, mitigated, or handed off to external entities. 

## Strict Transition Constraints & Validations
- State transitions are managed using strict Form selections bound closely to Django's native Object Relational Mapping (ORM) models.
- **The Core Block Transition Rule:**
  - Transitioning from *Any State* -> `RESOLVED` is explicitly blocked unless the user satisfies the strict length rules placed on the `resolution_notes` field. 
  - (Implemented specifically via overriding the Django `clean()` validation rules inside `school_app/models.py`).