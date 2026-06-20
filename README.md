# Attendance Management System

A Streamlit-based attendance tracking app for small classrooms and training sessions.

This app combines role-based user access, student registration, attendance logging, and a webcam-based face recognition helper to simplify attendance management.

## How the App Works

- Users sign in with role-based access: **admin** and **lecturer**.
- Admins and lecturers can register students and store student records locally in `data/students.pkl`.
- Attendance is saved as daily CSV files under `data/attendance/`, with one file per date.
- Students can be registered with a face photo uploaded from their device or captured from the webcam.
- A separate face recognition helper launches from the app to detect faces with a local webcam and mark attendance automatically.
- The app also supports syncing student records from a university CSV export or SIS API endpoint.
- Attendance reports are displayed inside the app and can be exported as CSV.

## Features

- Secure login and user registration
- Admin-only user management
- Dashboard with total students, present/absent counts, and score analytics
- Manual attendance marking and undo support
- Student list with engagement scoring, score updates, and removal
- Student registration with photo upload or webcam capture
- Bulk import students from CSV
- University SIS sync via CSV or API
- Downloadable app backup ZIP
- Attendance reporting with charts and export

## Getting Started

1. Activate the Python virtual environment:

```powershell
cd C:\Users\user\Desktop\Projects\attendance_system
myenv\Scripts\activate
```

2. Install dependencies if needed:

```powershell
pip install -r requirements.txt
```

3. Run the Streamlit app:

```powershell
python -m streamlit run app.py --server.port 8501 --server.headless true
```

4. Open the app in your browser:

```text
http://localhost:8501
```

## Step-by-Step Usage

1. Open the app and log in with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`

2. Register a student:
   - Go to **Register Student**.
   - Enter the student's name, optional student ID, email, and initial engagement score.
   - Upload a face photo or capture one with the webcam.
   - Submit the form to save the student record.

3. Mark attendance manually:
   - Go to **Mark Attendance**.
   - Use the search box to find the student.
   - Click **Mark** to set a student present.
   - Optionally use **Mark All Present** to mark every registered student.

4. Use face recognition attendance:
   - Open **Face Recognition**.
   - Click **Launch Face Recognition Helper**.
   - A separate helper window will open and use the webcam for face capture.
   - Follow the helper instructions to enroll faces and mark attendance.

5. Sync students from a university system:
   - Go to **University Sync**.
   - Upload a CSV file with columns `Name`, `StudentID`, and `Email`.
   - Or provide a SIS API endpoint that returns CSV or JSON.
   - Sync the imported records into the app.

6. Review attendance and export reports:
   - Go to **Reports**.
   - Select a date and view the attendance summary.
   - Download the CSV export for the selected attendance date.

## Important Notes

- The app stores data locally in the `data/` folder.
- Face photos are saved in `data/faces/`.
- Daily attendance records are saved in `data/attendance/`.
- If you run the face recognition helper, make sure your machine has an accessible webcam.

## File Structure

- `app.py`: main Streamlit application and UI logic
- `attendance_system_deepface.py`: face recognition helper script
- `requirements.txt`: project dependencies
- `data/`: local storage for users, students, face images, attendance records, and sync logs
- `templates/`: HTML templates for optional web pages

## Default Admin Account

- Username: `admin`
- Password: `admin123`

If you want, create a new admin or lecturer account from the login/register page after first launch.

## Deploy to Render (Quick Start)

This project includes a `render.yaml` manifest so Render can auto-detect and deploy the app.

Steps to deploy:

1. Push your changes to GitHub (already done if you followed earlier steps).
2. Sign in to https://render.com and connect your GitHub account.
3. Create a new service and select this repository (`Students_attendance_system`).
   - Render will read `render.yaml` and use the provided `buildCommand` and `startCommand`.
4. Ensure the service is set to deploy from the `main` branch.

Streamlit will use the port provided by Render via the `$PORT` environment variable.

If you prefer to create the service manually, use these settings:

```text
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port $PORT --server.headless true
Environment: Python
Branch: main
```

After creating the service, trigger a manual deploy (or wait for auto-deploy) and open the service URL Render provides.

If you'd like, I can create the Render service for you via the Render API next — would you like me to do that?
