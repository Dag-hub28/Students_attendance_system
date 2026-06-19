# Attendance System with Authentication

This project now includes a basic authentication system built with Flask.

## Features Added:
- User registration and login
- Role-based access (student, lecturer, admin)
- Protected dashboard showing attendance summaries
- Admin panel to view all users
- Manual attendance marking for lecturers/admins
- Basic analytics dashboard
- Email notifications for weekly reports
- **Password reset functionality**

## How to Run:
1. Activate the virtual environment: `myenv\Scripts\activate` (or `.venv\Scripts\activate`)
2. Run the app: `python app.py`
3. Open http://localhost:5000 in your browser

## Usage:
- Register a new user at /register (now includes email)
- Login at /login
- Access dashboard at /dashboard
- Lecturers/Admins can mark attendance at /mark_attendance
- View analytics at /analytics
- Send weekly email report at /send_report
- Admins can access /admin

## Face Enrollment for Students:
1. Login as a student
2. Click "Register Face" on the dashboard
3. Upload a clear photo of your face or use the camera
4. Your face will be enrolled for automatic attendance recognition

## Email Setup:
- Configure SMTP settings in `send_email()` function
- Use Gmail or another provider
- Replace placeholder credentials with real ones

## Security Notes:
- Passwords are hashed using Werkzeug
- User data is stored in users.pkl (not secure for production)
- Use a proper database like SQLite or PostgreSQL for production
- Password reset tokens expire after 1 hour

## Next Steps:
- Add more advanced analytics and reporting