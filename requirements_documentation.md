# Requirements Documentation

## Critical Weaknesses of Current Attendance Systems

Based on stakeholder interviews and survey responses, the following critical weaknesses have been identified:

### Weakness 1: Identity Spoofing / Proxy Attendance
- **Description**: Students can mark attendance for absent peers without verification
- **Evidence**: 70% of students surveyed reported observing proxy attendance
- **Impact**: Zero verification of actual student presence during class
- **Current Rate**: Estimated 25-40% of online sessions affected

### Weakness 2: False Negatives (Present Marked Absent)
- **Description**: Legitimate students marked absent due to technical issues
- **Evidence**: 45% of students experienced false negatives; 15% reported weekly technical failures
- **Impact**: Academic penalty for legitimate attendees
- **Time Cost**: 5-10 minutes per class to resolve disputes

### Weakness 3: Manual Verification Overhead
- **Description**: Lecturers spend excessive time on manual attendance tasks
- **Evidence**: Average 8-12 minutes per class spent on attendance verification
- **Impact**: Reduced teaching time, increased administrative burden
- **Scale**: Multiplies across classes (20+ hours per lecturer per semester for 30 students)

---

## Functional Requirements

### FR-1: User Authentication
- FR-1.1: User registration with email verification
- FR-1.2: Role-based access (student, lecturer, admin)
- FR-1.3: Secure password storage with hashing

### FR-2: Face Enrollment
- FR-2.1: Student face registration via camera upload
- FR-2.2: Multiple face samples per student for accuracy
- FR-2.3: Face quality validation

### FR-3: Face Recognition
- FR-3.1: Real-time face detection and recognition
- FR-3.2: Accuracy ≥90% on diverse dataset
- FR-3.3: Response time <3 seconds

### FR-4: Attendance Tracking
- FR-4.1: Automatic attendance marking on face detection
- FR-4.2: Timestamp recording
- FR-4.3: Class/session association

### FR-5: Continuous Monitoring
- FR-5.1: Periodic re-verification every 10 minutes
- FR-5.2: Presence status tracking
- FR-5.3: Absence alerts after 15 minutes

---

## Non-Functional Requirements

### NFR-1: Security
- NFR-1.1: AES-256 encryption for stored face data
- NFR-1.2: HTTPS for all communications
- NFR-1.3: Secure token-based session management

### NFR-2: Privacy
- NFR-2.1: Informed consent workflow before enrollment
- NFR-2.2: Data deletion upon request
- NFR-2.3: GDPR/Ethics Board compliance

### NFR-3: Performance
- NFR-3.1: Face recognition response <3 seconds
- NFR-3.2: Support 30+ concurrent students
- NFR-3.3: 99% uptime during scheduled classes

### NFR-4: Usability
- NFR-4.1: Mobile-responsive interface
- NFR-4.2: One-click enrollment process
- NFR-4.3: Clear error messages