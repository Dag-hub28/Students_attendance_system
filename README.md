# Attendance Management System

A Streamlit-based attendance tracking app with:

- Login + role-based access (admin/lecturer)
- Dashboard with attendance metrics
- Manual attendance marking
- Student registration with photo upload or webcam capture
- Face recognition helper for webcam-driven attendance
- University CSV import and SIS API syncing
- Attendance reports and exports
- User management for admin accounts
- Settings page with backup export

## Getting Started

1. Activate the Python virtual environment:

```powershell
cd C:\Users\user\Desktop\attendance_system
myenv\Scripts\activate
```

2. Install dependencies if needed:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python -m streamlit run app.py --server.port 8501 --server.headless true
```

4. Open the app in your browser:

```text
http://localhost:8501
```

## Usage

- Use the default admin account: `admin` / `admin123`
- Register students via the **Register Student** page.
- Capture a face photo from webcam or upload an image file.
- Use **Mark Attendance** for manual marking.
- Launch the **Face Recognition** helper for webcam-based attendance.
- Sync students via CSV or SIS API on the **University Sync** page.
- View reports and download CSV exports on the **Reports** page.
- Admins can manage users in the **Manage Users** page.

## File Structure

- `app.py`: main Streamlit application
- `attendance_system_deepface.py`: local face recognition helper
- `data/`: storage for attendance CSVs, user/student data, face images, logs
- `requirements.txt`: Python dependencies
- `.gitignore`: files and folders to ignore

## Notes

- Face recognition uses OpenCV and DeepFace.
- The helper may open a separate camera window when launched.
- `data/` includes attendance files and face photos; do not commit it to source control.
