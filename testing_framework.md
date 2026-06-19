# Model Testing Framework

## Accuracy Testing Protocol

### Test Dataset Requirements
- **Sample Size**: 30+ student volunteers
- **Lighting Conditions**:
  - Well-lit (office/lecture hall)
  - Dim lighting (evening study)
  - Backlit (window behind)
  - Mixed lighting (natural + artificial)
- **Angles**: Front-facing, slight angles (±15°)

### Accuracy Metrics
- **Target**: ≥90% top-1 accuracy
- **Response Time**: <3 seconds per verification
- **False Positive Rate**: <2%
- **False Negative Rate**: <5%

---

## Continuous Monitoring Testing

### Verification Interval Test
1. Simulate 60-minute class session
2. Verify student identity every 10 minutes
3. Measure:
   - Detection consistency across intervals
   - Average response time
   - Memory/CPU usage

### Performance Script
```python
import time
import cv2

def benchmark_recognition(video_source=0, duration_minutes=60):
    """Benchmark recognition performance"""
    cap = cv2.VideoCapture(video_source)
    start = time.time()
    
    while (time.time() - start) < (duration_minutes * 60):
        ret, frame = cap.read()
        if ret:
            t0 = time.time()
            detected = live_monitor.recognize_face(frame)
            response_time = time.time() - t0
            
            print(f"Detected: {detected}, Time: {response_time:.3f}s")
    
    cap.release()
```

---

## Pilot Testing Protocol

### Class 1: Small Group (10-15 students)
- **Duration**: 50-minute session
- **Metrics Collected**:
  - Recognition accuracy per student
  - Connection stability
  - User experience feedback

### Class 2: Large Group (30+ students)
- **Duration**: 50-minute session
- **Metrics Collected**:
  - Concurrent performance
  - Server resource usage
  - Scalability assessment

### Data Collection Template
```
Student ID | Lighting | Accuracy | Response (ms) | Issues | Comments
-------------------------------------------------------------------
S001       | Good    | 95%      | 1.2s          | None   |  
S002       | Dim     | 88%      | 2.1s          | Blur   |  
...
```

---

## Survey: User Acceptance

### Post-Pilot Questionnaire
1. How reliable was the attendance system? (1-5 scale)
2. Did you experience any technical issues? (Yes/No + details)
3. Was the face enrollment process clear? (Yes/No)
4. Would you recommend this system for regular use? (Yes/No)
5. Any privacy concerns? (Open text)

### Success Criteria
- ≥80% positive user feedback
- ≤5% dropout rate during sessions
- ≥90% accuracy maintained at scale