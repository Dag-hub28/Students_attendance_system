# AI-Driven Attendance Verification System - Project Plan

## Executive Summary
Design and develop an AI-driven online attendance verification system with facial recognition, continuous monitoring, and privacy-by-design principles.

## Current System Analysis

### Existing Codebase Components:
- `app.py`: Flask web application with user authentication
- `live_monitoring.py`: Face recognition using OpenCV Haar Cascade + DeepFace
- Templates: login, dashboard, face enrollment, camera monitoring
- Face database stored in pickle files

## Objectives Timeline & Implementation

### Month 1: Stakeholder Research & Requirements Analysis
**Objective 1**: Investigate and document at least 3 critical weaknesses through stakeholder interviews and surveys

#### Deliverables:
1. Stakeholder Interview Guide
2. Survey Questionnaire
3. Requirements Documentation
4. Gap Analysis Report

### Month 2-3: AI Facial Recognition Model Development
**Objective 2**: Develop AI facial recognition model with ≥90% accuracy on 30+ volunteers under varied lighting

#### Technical Requirements:
- Dataset: 30+ student volunteers
- Lighting conditions: varied (indoor, outdoor, low-light)
- Accuracy target: ≥90%
- Response time: <3 seconds per verification

### Month 4: Continuous Presence Monitoring
**Objective 3**: Implement continuous monitoring with 10-minute re-verification intervals

### Month 5: Pilot Testing & Deployment
**Objective 4**: Pilot testing in 2 university classes (30+ students)
**Objective 5**: Privacy-by-design implementation (AES-256, consent workflows, data deletion)

---

## Technical Architecture

### Face Recognition Pipeline:
1. Face Detection → Haar Cascade / DNN
2. Face Alignment → Preprocessing
3. Feature Extraction → DeepFace embeddings
4. Matching → Cosine similarity threshold

### Security Architecture:
- AES-256 encryption for stored face data
- Consent management system
- Automated data deletion policies
- GDPR/Ethics compliance

## Development Milestones

| Week | Task |
|------|------|
| 1-2 | Stakeholder interviews, survey design |
| 3-4 | Literature review, requirements finalized |
| 5-8 | Model training, dataset collection |
| 9-12 | Continuous monitoring implementation |
| 13-16 | Pilot testing, Ethics approval |
| 17-20 | Deployment, documentation |