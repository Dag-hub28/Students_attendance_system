# Ethics Review Board Submission Package

## Protocol Title
AI-Driven Online Attendance Verification System: Identity Authentication and Continuous Presence Monitoring

## Principal Investigator
[Name], [Department], [University]

## Study Summary
Development and pilot testing of an AI facial recognition system for university online class attendance verification. The system captures student face data to verify identity during synchronous online sessions.

---

## Section 1: Research Objectives

### Primary Objectives
1. Identify critical weaknesses in current online attendance systems through stakeholder research
2. Develop AI facial recognition achieving ≥90% accuracy on 30+ student volunteers
3. Implement continuous monitoring with 10-minute verification intervals
4. Conduct pilot testing in actual university classes
5. Ensure privacy-by-design compliance

---

## Section 2: Methodology

### Participant Recruitment
- **Target**: 30+ student volunteers from university courses
- **Inclusion Criteria**: Age 18+, enrolled student, consent to participate
- **Exclusion Criteria**: None identified

### Data Collection
- **Face Images**: 3-5 images per participant under varied lighting conditions
- **Performance Metrics**: Recognition accuracy, response time, false positive/negative rates
- **Survey Responses**: Pre/post implementation feedback

---

## Section 3: Privacy & Data Protection

### Consent Process
1. **Informed Consent Form** provided before face enrollment
2. **Purpose**: Attendance verification only
3. **Voluntary Participation**: Opt-out anytime
4. **Data Minimization**: Only store necessary facial features

### Data Storage
- **Encryption**: AES-256 for stored face data
- **Access Control**: Limited to system administrators
- **Retention**: 
  - Research phase: 12 months post-completion
  - Automatic deletion upon request

### Data Deletion
- Participants can request full deletion at any time
- `/delete_my_face_data` API endpoint for self-service deletion
- Admin deletion capability via `/admin/delete_student_face/<id>`

---

## Section 4: Risk Assessment

### Potential Risks
| Risk | Mitigation |
|------|-----------|
| Privacy breach | AES-256 encryption, access controls |
| Identity spoofing | Multi-sample verification, periodic re-checks |
| False negatives | Threshold tuning, manual override |
| Bias in AI | Diverse dataset, accuracy monitoring |

### Minimizing Risks
- Face data used ONLY for attendance verification
- No sharing with third parties
- Secure development practices
- Regular security audits

---

## Section 5: Consent Form

```
CONSENT FOR FACE DATA COLLECTION

I understand that:
1. My facial data will be used ONLY for attendance verification during online classes
2. Data is encrypted and stored securely using AES-256
3. I can request deletion of my data at any time
4. Data will be deleted automatically after graduation
5. No third-party sharing will occur

By enrolling my face, I consent to this data collection.
Signature: _________________ Date: _______
```

---

## Section 6: Timeline

| Activity | Month |
|----------|-------|
| Stakeholder research | Month 1 |
| Model development | Months 2-3 |
| Continuous monitoring | Month 4 |
| Ethics approval (this submission) | Month 2 |
| Pilot testing | Month 5 |

## Certification
I certify that this research has been reviewed and approved by the Ethics Review Board.

**ERB Chair Signature**: ___________________ **Date**: _________

**Approval Reference**: ERB-2026-ATT-001