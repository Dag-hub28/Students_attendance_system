# Run Instructions - Attendance System

## Prerequisites
- Python 3.11+ 
- Webcam for face enrollment

## Start Application
```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Run Flask server
.venv\Scripts\python.exe app.py

# 3. Open browser to:
# http://localhost:5000
```

## Quick Testing Flow
1. **Register** → Create student account
2. **Login** → Access dashboard
3. **Enroll Face** → Capture and enroll your face
4. **Test Recognition** → Go to `/test_recognition` to verify detection
5. **Run Test Script** → `.venv\Scripts\python.exe test_recognition.py`

## For 30+ Face Dataset Collection
```bash
# Quick collection mode:
.venv\Scripts\python.exe collect_faces.py
# Enter name and number of samples (2-3 per person recommended)
```

## Test Commands
```bash
# Run basic recognition test
.venv\Scripts\python.exe test_recognition.py

# Run live test (60 seconds)
.venv\Scripts\python.exe test_accuracy.py live 60

# Run benchmark (100 frames)
.venv\Scripts\python.exe test_accuracy.py benchmark 100
```

## Current Status
- Response time: <10ms (target: <3s) ✓
- Accuracy: Need real faces to measure
- Missing: 30+ volunteer face samples