# Problem Statement

**Population Studied:** Middle and High School youth (Ages 12-18) in the Tunisian educational system, particularly those attending public institutions where counselor-to-student ratios may be strained.

**Targeted Problem/Behavior:** Identifying early indicators of school disengagement, distress, or personal tracking issues. Historically, absent behaviors and subtle classroom distress signs are siloed with individual teachers, missing the wider context preventing a counselor from intervening prior to a total dropout or mental escalation.

**Decision Maker:** School Counselors and the School Principal evaluate the structural and singular trends using the platform designed outputs.

**Operational Workflow (Step-by-Step):**
1. **Intake:** Teachers log daily attendance and behavior flags for assigned students.
2. **Detection:** System algorithms evaluate inputs (absence counts or flags) and automatically create `NEW` Intervention Cases.
3. **Assessment:** Counselors review active cases, transition status to `IN_REVIEW`, and document initial findings.
4. **Planning:** Counselors formulate an `INTERVENTION` plan and set a mandatory `follow_up_date`.
5. **Monitoring:** System monitors deadlines; if missed, case escalates to `FOLLOW_UP_MISSED`.
6. **Resolution:** Counselor conducts follow-up, logs `resolution_notes`, and closes the case as `RESOLVED`.

**Expected Value:** Transforming fragmented paper and mental notes into a centralized, objective tracking ecosystem. This accelerates the intervention timeline drastically, centralizes case tracking, prevents students from falling through systemic cracks, and structurally reduces dropout and absenteeism rates.

**Validation Rule:** The platform evaluates correctness by securely barring unauthorized roles from reading or writing outside their designated scope, and mathematically tracking valid progression through mandatory system validation steps (e.g. requiring explicit resolution text closures to prevent shadow case dropping).