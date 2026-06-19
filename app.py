import streamlit as st
import io
import sys
import subprocess
import zipfile
import pandas as pd
import os
import json
import pickle
import hashlib
import csv
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
from attendance_system_deepface import SimpleAttendanceSystem

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
    }
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
DATA_DIR = "data"
ATTENDANCE_DIR = os.path.join(DATA_DIR, "attendance")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.pkl")
FACES_DIR = os.path.join(DATA_DIR, "faces")
UNIVERSITY_SYNC_LOG = os.path.join(DATA_DIR, "university_sync.log")

# ─── Directory Setup ─────────────────────────────────────────────────────────
def ensure_data_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    os.makedirs(FACES_DIR, exist_ok=True)

ensure_data_dirs()

# ─── Helper Functions ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    ensure_data_dirs()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Default admin account
    default = {
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "name": "Administrator",
            "created": datetime.now().strftime("%Y-%m-%d")
        }
    }
    save_users(default)
    return default

def save_users(users: dict):
    ensure_data_dirs()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def load_students() -> dict:
    ensure_data_dirs()
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list):
                    return {
                        "students": data,
                        "scores": {s: 100.0 for s in data},
                        "info": {}
                    }
        except Exception:
            pass
    return {"students": [], "scores": {}, "info": {}}

def save_students(data: dict):
    ensure_data_dirs()
    with open(STUDENTS_FILE, "wb") as f:
        pickle.dump(data, f)

def get_attendance_files() -> list:
    ensure_data_dirs()
    return sorted(
        [f for f in os.listdir(ATTENDANCE_DIR) if f.startswith("attendance_") and f.endswith(".csv")],
        reverse=True
    )

def load_attendance(filename: str) -> pd.DataFrame:
    full_path = os.path.join(ATTENDANCE_DIR, filename) if not filename.startswith(ATTENDANCE_DIR) else filename
    try:
        df = pd.read_csv(full_path)
        return df
    except Exception:
        return pd.DataFrame(columns=["Name", "Time", "Date", "Engagement Score"])

def mark_attendance_csv(name: str, score: float = 100.0) -> bool:
    ensure_data_dirs()
    filename = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
    # Check if already marked today
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        if name in df["Name"].values:
            return False  # Already marked
    
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Time", "Date", "Engagement Score"])
        writer.writerow([
            name,
            datetime.now().strftime("%H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d"),
            f"{score:.1f}%"
        ])
    return True

def authenticate(username: str, password: str) -> dict | None:
    users = load_users()
    if username in users:
        if users[username]["password"] == hash_password(password):
            return users[username]
    return None
def log_university_sync(message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(UNIVERSITY_SYNC_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")

def parse_university_csv(file) -> list[dict]:
    try:
        df = pd.read_csv(file)
        rows = []
        for i, row in df.iterrows():
            name = str(row.get("Name", "")).strip()
            student_id = str(row.get("StudentID", "")).strip()
            email = str(row.get("Email", "")).strip()
            if name:
                rows.append({"name": name, "id": student_id, "email": email})
        return rows
    except Exception as e:
        st.error(f"Invalid university CSV format: {e}")
        return []

def merge_university_students(new_students: list[dict], data: dict) -> tuple[int, int]:
    added = 0
    skipped = 0
    if "info" not in data:
        data["info"] = {}
    for record in new_students:
        name = record["name"]
        if name in data.get("students", []):
            skipped += 1
            continue
        data["students"].append(name)
        data["scores"][name] = 100.0
        data["info"][name] = {
            "id": record.get("id", ""),
            "email": record.get("email", ""),
            "registered": datetime.now().strftime("%Y-%m-%d"),
            "source": "university"
        }
        added += 1
    return added, skipped

def fetch_students_from_university_api(api_url: str) -> list[dict]:
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        content = response.text

        if "text/csv" in content_type or content.strip().startswith("Name,"):
            df = pd.read_csv(io.StringIO(content))
        else:
            df = pd.read_json(io.StringIO(content))

        rows = []
        if "Name" in df.columns:
            for _, row in df.iterrows():
                name = str(row.get("Name", "")).strip()
                sid = str(row.get("StudentID", "")).strip()
                email = str(row.get("Email", "")).strip()
                if name:
                    rows.append({"name": name, "id": sid, "email": email})
        return rows
    except Exception:
        return []

# ─── Session State Init ───────────────────────────────────────────────────────

def init_session():
    defaults = {
        "logged_in": False,
        "username": None,
        "user_info": None,
        "page": "login",
        "attendance_today": set(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ─── Login Page ───────────────────────────────────────────────────────────────

def show_login():
    st.markdown('<div class="main-header">🎓 Attendance Management System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Secure • Smart • Simple</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back!")
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login →", type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_info = user
                        st.session_state.page = "dashboard"
                        st.success(f"Welcome back, {user['name']}! 👋")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
            
            st.markdown("---")
            st.info("**Default Admin:** username: `admin` | password: `admin123`")
        
        with tab2:
            st.markdown("### Create Account")
            with st.form("register_form"):
                new_name = st.text_input("👤 Full Name", placeholder="Your full name")
                new_username = st.text_input("🆔 Username", placeholder="Choose a username")
                new_role = st.selectbox("🎭 Role", ["lecturer", "admin"])
                new_password = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
                confirm_password = st.text_input("🔒 Confirm Password", type="password")
                reg_submitted = st.form_submit_button("Create Account →", type="primary")
            
            if reg_submitted:
                users = load_users()
                if not all([new_name, new_username, new_password]):
                    st.error("All fields are required.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif new_username in users:
                    st.error(f"Username '{new_username}' already exists.")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "role": new_role,
                        "name": new_name,
                        "created": datetime.now().strftime("%Y-%m-%d")
                    }
                    save_users(users)
                    st.success(f"✅ Account created for {new_name}! You can now login.")

# ─── Sidebar ──────────────────────────────────────────────────────────────────

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_info['name']}")
        st.markdown(f"*{st.session_state.user_info['role'].capitalize()}*")
        st.markdown("---")
        
        pages = {
            "📊 Dashboard": "dashboard",
            "✅ Mark Attendance": "mark_attendance",
            "🎥 Face Recognition": "face_recognition",
            "📋 Student List": "students",
            "➕ Register Student": "register_student",
            "🧭 University Sync": "university_integration",
            "⚙️ Settings": "settings",
            "📈 Reports": "reports",
        }
        
        if st.session_state.user_info["role"] == "admin":
            pages["⚙️ Manage Users"] = "manage_users"
        
        for label, page_key in pages.items():
            if st.button(label, use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session()
            st.rerun()

# ─── Dashboard Page ───────────────────────────────────────────────────────────

def show_dashboard():
    st.markdown("## 📊 Dashboard")
    
    data = load_students()
    students = data.get("students", [])
    scores = data.get("scores", {})
    
    today_file = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
    today_df = load_attendance(today_file) if os.path.exists(today_file) else pd.DataFrame()
    present_today = len(today_df) if not today_df.empty else 0
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Students", len(students))
    with col2:
        st.metric("✅ Present Today", present_today)
    with col3:
        absent = len(students) - present_today
        st.metric("❌ Absent Today", absent)
    with col4:
        pct = (present_today / len(students) * 100) if students else 0
        st.metric("📊 Attendance Rate", f"{pct:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Recent Attendance Files")
        files = get_attendance_files()[:7]
        if files:
            records = []
            for f in files:
                date_str = f.replace("attendance_", "").replace(".csv", "")
                try:
                    formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                except Exception:
                    formatted = f
                df_tmp = load_attendance(f)
                records.append({"Date": formatted, "Records": len(df_tmp)})
            df_files = pd.DataFrame(records)
            fig = px.bar(df_files, x="Date", y="Records", 
                        title="Attendance by Day",
                        color="Records", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance records found yet.")
    
    with col2:
        st.subheader("🌟 Engagement Score Distribution")
        if scores:
            score_vals = list(scores.values())
            fig = px.histogram(x=score_vals, nbins=10,
                              labels={"x": "Engagement Score (%)", "y": "Number of Students"},
                              title="Score Distribution",
                              color_discrete_sequence=["#667eea"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement scores yet.")
    
    # Today's attendance table
    if not today_df.empty:
        st.subheader(f"📋 Today's Attendance — {datetime.now().strftime('%A, %B %d %Y')}")
        st.dataframe(today_df, use_container_width=True, hide_index=True)

# ─── Mark Attendance Page ─────────────────────────────────────────────────────

def show_mark_attendance():
    st.markdown("## ✅ Mark Attendance")
    
    data = load_students()
    students = data.get("students", [])
    scores = data.get("scores", {})
    
    if not students:
        st.warning("⚠️ No students registered yet. Go to **Register Student** first.")
        return
    
    today_file = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
    already_marked = set()
    if os.path.exists(today_file):
        df = pd.read_csv(today_file)
        already_marked = set(df["Name"].tolist())
    
    st.markdown(f"📅 **Date:** {datetime.now().strftime('%A, %B %d, %Y')}")
    st.markdown(f"📊 **Present:** {len(already_marked)}/{len(students)}")
    st.markdown("---")
    
    # Quick mark all button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✅ Mark All Present", type="primary"):
            count = 0
            for student in students:
                if student not in already_marked:
                    if mark_attendance_csv(student, scores.get(student, 100.0)):
                        count += 1
            st.success(f"✅ Marked {count} students present!")
            st.rerun()
    
    st.markdown("---")
    
    # Search box
    search = st.text_input("🔍 Search student", placeholder="Type name to filter...")
    
    filtered = [s for s in students if search.lower() in s.lower()] if search else students
    
    # Table with checkboxes
    cols = st.columns([0.5, 2, 1.5, 1.5, 1.5])
    cols[0].markdown("**#**")
    cols[1].markdown("**Student Name**")
    cols[2].markdown("**Score**")
    cols[3].markdown("**Status**")
    cols[4].markdown("**Action**")
    st.divider()
    
    for i, student in enumerate(filtered, 1):
        score = scores.get(student, 100.0)
        is_present = student in already_marked
        
        cols = st.columns([0.5, 2, 1.5, 1.5, 1.5])
        cols[0].write(f"{i}")
        cols[1].write(f"**{student}**")
        cols[2].write(f"{score:.1f}%")
        
        if is_present:
            cols[3].markdown("✅ Present")
            if cols[4].button("↩️ Undo", key=f"undo_{student}"):
                # Remove from CSV
                if os.path.exists(today_file):
                    df = pd.read_csv(today_file)
                    df = df[df["Name"] != student]
                    df.to_csv(today_file, index=False)
                    st.success(f"Removed {student} from today's attendance.")
                    st.rerun()
        else:
            cols[3].markdown("❌ Absent")
            if cols[4].button("✅ Mark", key=f"mark_{student}"):
                mark_attendance_csv(student, score)
                st.success(f"✅ {student} marked present!")
                st.rerun()

# ─── Students Page ─────────────────────────────────────────────────────────────

def show_students():
    st.markdown("## 📋 Student List")
    
    data = load_students()
    students = data.get("students", [])
    scores = data.get("scores", {})
    info = data.get("info", {})
    
    if not students:
        st.warning("No students registered. Go to **Register Student**.")
        return
    
    # Stats
    col1, col2, col3 = st.columns(3)
    avg_score = sum(scores.values()) / len(scores) if scores else 0
    col1.metric("👥 Total", len(students))
    col2.metric("📊 Avg Score", f"{avg_score:.1f}%")
    col3.metric("🌟 Top Score", f"{max(scores.values()):.1f}%" if scores else "N/A")
    
    st.markdown("---")
    
    # Build dataframe
    rows = []
    for student in students:
        score = scores.get(student, 100.0)
        student_info = info.get(student, {})
        if score >= 90:
            rating = "🌟 Excellent"
        elif score >= 75:
            rating = "👍 Good"
        elif score >= 60:
            rating = "👌 Fair"
        elif score >= 40:
            rating = "⚠️ Warning"
        else:
            rating = "🔴 Critical"
        rows.append({
            "Name": student,
            "Student ID": student_info.get("id", "N/A"),
            "Email": student_info.get("email", "N/A"),
            "Engagement Score": f"{score:.1f}%",
            "Rating": rating
        })
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Update score section
    st.markdown("---")
    st.subheader("📝 Update Engagement Score")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_student = st.selectbox("Select Student", students)
    with col2:
        change = st.number_input("Score Change (%)", min_value=-50, max_value=50, value=5)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Update Score", type="primary"):
            old = scores.get(selected_student, 100.0)
            new_score = max(0, min(100, old + change))
            data["scores"][selected_student] = new_score
            save_students(data)
            st.success(f"✅ {selected_student}: {old:.1f}% → {new_score:.1f}%")
            st.rerun()
    
    # Delete student
    st.markdown("---")
    st.subheader("🗑️ Remove Student")
    col1, col2 = st.columns([2, 1])
    with col1:
        del_student = st.selectbox("Select to remove", students, key="del_select")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Remove", type="secondary"):
            data["students"].remove(del_student)
            data["scores"].pop(del_student, None)
            data.get("info", {}).pop(del_student, None)
            save_students(data)
            st.success(f"✅ Removed {del_student}")
            st.rerun()

# ─── Register Student Page ────────────────────────────────────────────────────

def show_register_student():
    st.markdown("## ➕ Register New Student")
    
    data = load_students()
    
    os.makedirs(FACES_DIR, exist_ok=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Student Information")
        with st.form("register_student_form"):
            student_name = st.text_input("Full Name *", placeholder="e.g. John Doe")
            student_id = st.text_input("Student ID", placeholder="e.g. S001")
            student_email = st.text_input("Email", placeholder="e.g. john@university.ac.ke")
            initial_score = st.slider("Initial Engagement Score", 0, 100, 100)
            
            st.markdown("---")
            face_photo = st.file_uploader(
                "📸 Upload Face Photo (optional)",
                type=["jpg", "jpeg", "png"],
                help="Upload a clear photo of the student's face for face recognition"
            )
            camera_photo = st.camera_input("📷 Capture Face with Webcam (optional)")
            
            submitted = st.form_submit_button("Register Student →", type="primary")
        
        if submitted:
            if not student_name.strip():
                st.error("Student name is required.")
            elif student_name in data.get("students", []):
                st.error(f"Student '{student_name}' already registered.")
            else:
                # Add to students list
                data["students"].append(student_name)
                data["scores"][student_name] = float(initial_score)
                if "info" not in data:
                    data["info"] = {}
                data["info"][student_name] = {
                    "id": student_id,
                    "email": student_email,
                    "registered": datetime.now().strftime("%Y-%m-%d")
                }
                
                student_photo = face_photo or camera_photo
                if student_photo:
                    image_bytes = student_photo.getvalue()
                    photo_filename = os.path.join(
                        FACES_DIR,
                        f"{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    with open(photo_filename, "wb") as f:
                        f.write(image_bytes)
                    data["info"][student_name]["face_photo"] = photo_filename
                    st.success(f"✅ {student_name} registered with face photo!")
                else:
                    st.success(f"✅ {student_name} registered successfully!")
                
                save_students(data)
                st.rerun()
    
    with col2:
        st.subheader("👥 Bulk Register (CSV Import)")
        st.markdown("""
        Upload a CSV file with student names:
        
        **Format:**
        ```
        Name,StudentID,Email
        John Doe,S001,john@uni.ac.ke
        Jane Smith,S002,jane@uni.ac.ke
        ```
        """)
        
        csv_file = st.file_uploader("Upload CSV", type=["csv"])
        
        if csv_file:
            try:
                df = pd.read_csv(csv_file)
                st.write("**Preview:**")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
                
                if st.button("Import Students", type="primary"):
                    if "info" not in data:
                        data["info"] = {}
                    count = 0
                    skipped = 0
                    for _, row in df.iterrows():
                        name = str(row.get("Name", row.iloc[0])).strip()
                        if name and name not in data["students"]:
                            data["students"].append(name)
                            data["scores"][name] = 100.0
                            data["info"][name] = {
                                "id": str(row.get("StudentID", row.get("student_id", ""))),
                                "email": str(row.get("Email", row.get("email", ""))),
                                "registered": datetime.now().strftime("%Y-%m-%d")
                            }
                            count += 1
                        else:
                            skipped += 1
                    save_students(data)
                    st.success(f"✅ Imported {count} students. Skipped {skipped} duplicates.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        
        # Current count
        st.markdown("---")
        st.info(f"📋 Currently registered: **{len(data.get('students', []))} students**")
        
        # Show recently registered
        info_dict = data.get("info", {})
        if info_dict:
            st.subheader("📅 Recently Registered")
            recent = []
            for name, d in info_dict.items():
                recent.append({"Name": name, "ID": d.get("id",""), "Registered": d.get("registered","")})
            df_recent = pd.DataFrame(recent).sort_values("Registered", ascending=False).head(5)
            st.dataframe(df_recent, use_container_width=True, hide_index=True)

# ─── University Integration Page ───────────────────────────────────────────────

def show_university_integration():
    st.markdown("## 🔗 University System Integration")
    st.markdown("Use this page to sync students from your university SIS export to this attendance app.")

    data = load_students()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1) Import university CSV")
        st.markdown("Upload a CSV from your university system with columns: Name, StudentID, Email.")
        uni_csv = st.file_uploader("University CSV", type=["csv"], key="uni_csv")
        if uni_csv:
            rows = parse_university_csv(uni_csv)
            st.info(f"📥 Parsed {len(rows)} student rows.")
            if st.button("Sync to Attendance System", key="sync_uni_csv"):
                added, skipped = merge_university_students(rows, data)
                save_students(data)
                st.success(f"✅ Synced {added} students, skipped {skipped} duplicates.")
                log_university_sync(f"CSV sync: added={added}, skipped={skipped}")
                st.experimental_rerun()

    with col2:
        st.subheader("2) SIS API sync")
        st.info("Sync student records from an HTTP endpoint that returns CSV or JSON.")
        api_url = st.text_input("SIS API endpoint URL", value="", placeholder="https://example.com/students.csv")
        if st.button("Fetch and Sync", key="fetch_sis_api"):
            if not api_url:
                st.error("Please enter a valid API URL.")
            else:
                rows = fetch_students_from_university_api(api_url)
                if not rows:
                    st.error("Could not fetch students from this API or invalid format.")
                else:
                    added, skipped = merge_university_students(rows, data)
                    save_students(data)
                    st.success(f"✅ Synced {added} students, skipped {skipped} duplicates.")
                    log_university_sync(f"API sync: url={api_url}, added={added}, skipped={skipped}")
                    st.experimental_rerun()

    st.markdown("---")
    st.subheader("Integration Log")
    if os.path.exists(UNIVERSITY_SYNC_LOG):
        with open(UNIVERSITY_SYNC_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-8:]
        st.text("".join(lines))
    else:
        st.info("No sync actions yet.")

# ─── Settings Page ───────────────────────────────────────────────────────────

def show_settings():
    st.markdown("## ⚙️ Settings & Help")
    st.markdown("Manage app storage, backup data, and review usage instructions.")

    st.subheader("Storage Paths")
    st.code(f"Data directory: {os.path.abspath(DATA_DIR)}", language="text")
    st.code(f"Attendance directory: {os.path.abspath(ATTENDANCE_DIR)}", language="text")
    st.code(f"Faces directory: {os.path.abspath(FACES_DIR)}", language="text")
    st.code(f"Users file: {os.path.abspath(USERS_FILE)}", language="text")
    st.code(f"Students file: {os.path.abspath(STUDENTS_FILE)}", language="text")
    st.code(f"Sync log: {os.path.abspath(UNIVERSITY_SYNC_LOG)}", language="text")

    st.markdown("---")
    st.subheader("Backup & Export")
    if st.button("Download app data backup", type="primary"):
        backup_buffer = io.BytesIO()
        with zipfile.ZipFile(backup_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(DATA_DIR):
                for filename in files:
                    path = os.path.join(root, filename)
                    zipf.write(path, os.path.relpath(path, DATA_DIR))
        backup_buffer.seek(0)
        st.download_button(
            label="⬇️ Download ZIP backup",
            data=backup_buffer,
            file_name="attendance_system_backup.zip",
            mime="application/zip",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("How to Use")
    st.markdown(
        "1. Register users using the login page.\n"
        "2. Add students through Register Student, upload or capture a face photo.\n"
        "3. Use Mark Attendance to take attendance manually.\n"
        "4. Use Face Recognition to open the helper app for webcam-based attendance.\n"
        "5. Sync students from university CSV or SIS API.\n"
        "6. Review reports and download attendance exports."
    )

    st.markdown("---")
    st.subheader("System Notes")
    st.info("Face recognition runs in a separate helper process and requires webcam/GPU support.")
    st.info("CSV uploads must include Name, StudentID, and Email columns.")
    st.info("If you need a browser-native camera capture, use the webcam capture field on Register Student.")

# ─── Face Recognition Page ───────────────────────────────────────────────────

def show_face_recognition():
    st.markdown("## 🎥 Face Recognition Attendance")
    st.markdown("Launch the local face-recognition helper to mark attendance using webcam.")
    st.info("This opens a separate window for face capture and recognition. Press 'q' to quit, 'r' to register additional faces.")

    if st.button("Launch Face Recognition Helper", type="primary"):
        script_path = os.path.join(os.path.dirname(__file__), "attendance_system_deepface.py")
        try:
            subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(__file__))
            st.success("✅ Face recognition helper started. Use the new window to capture faces.")
            st.info("If the window does not appear, make sure your system allows GUI windows from Python.")
        except Exception as e:
            st.error(f"Could not start the face recognition helper: {e}")

# ─── Reports Page ─────────────────────────────────────────────────────────────

def show_reports():
    st.markdown("## 📈 Attendance Reports")
    
    files = get_attendance_files()
    if not files:
        st.warning("No attendance records found.")
        return
    
    data = load_students()
    students = data.get("students", [])
    
    # File selector
    col1, col2 = st.columns([2, 2])
    with col1:
        selected = st.selectbox(
            "📅 Select Date",
            files,
            format_func=lambda x: x.replace("attendance_", "").replace(".csv", "")
                .replace("202", "202").strip()
        )
    
    df = load_attendance(selected)
    date_str = selected.replace("attendance_", "").replace(".csv", "")
    
    if df.empty:
        st.warning("No records in this file.")
        return
    
    # Fix score column to numeric
    if "Engagement Score" in df.columns:
        df["Score_Num"] = df["Engagement Score"].str.replace("%", "").astype(float)
    
    # Summary metrics
    st.markdown(f"### 📋 Report for {date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Present", len(df))
    col2.metric("Total Students", len(students) if students else "N/A")
    col3.metric("Absent", (len(students) - len(df)) if students else "N/A")
    
    if "Score_Num" in df.columns and not df.empty:
        col4.metric("Avg Engagement", f"{df['Score_Num'].mean():.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Arrival time chart
        if "Time" in df.columns:
            try:
                df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
                hour_counts = df["Hour"].value_counts().sort_index().reset_index()
                hour_counts.columns = ["Hour", "Count"]
                fig = px.bar(hour_counts, x="Hour", y="Count",
                            title="📊 Arrivals by Hour",
                            color="Count", color_continuous_scale="Viridis")
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass
    
    with col2:
        # Engagement score pie
        if "Score_Num" in df.columns:
            def categorize(s):
                if s >= 90: return "Excellent (90-100)"
                elif s >= 75: return "Good (75-89)"
                elif s >= 60: return "Fair (60-74)"
                elif s >= 40: return "Warning (40-59)"
                else: return "Critical (<40)"
            
            df["Category"] = df["Score_Num"].apply(categorize)
            cat_counts = df["Category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.pie(cat_counts, names="Category", values="Count",
                        title="🌟 Engagement Score Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Detailed Records")
    st.dataframe(df[["Name", "Time", "Date", "Engagement Score"]], 
                use_container_width=True, hide_index=True)
    
    # Download
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name=f"attendance_report_{date_str}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Multi-day analysis
    if len(files) > 1:
        st.markdown("---")
        st.subheader("📅 Multi-Day Attendance Trend")
        trend_data = []
        for f in files[:14]:  # Last 14 days
            d_str = f.replace("attendance_", "").replace(".csv", "")
            try:
                d_fmt = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:8]}"
                df_t = load_attendance(f)
                trend_data.append({"Date": d_fmt, "Present": len(df_t)})
            except Exception:
                pass
        
        if trend_data:
            df_trend = pd.DataFrame(trend_data).sort_values("Date")
            fig = px.line(df_trend, x="Date", y="Present",
                         title="Attendance Trend (Last 14 Days)",
                         markers=True,
                         color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig, use_container_width=True)

# ─── Manage Users Page (Admin only) ──────────────────────────────────────────

def show_manage_users():
    st.markdown("## ⚙️ Manage Users")
    
    users = load_users()
    
    # Display users table
    st.subheader("👥 All System Users")
    rows = []
    for username, info in users.items():
        rows.append({
            "Username": username,
            "Full Name": info.get("name", ""),
            "Role": info.get("role", ""),
            "Created": info.get("created", "")
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Add New User")
        with st.form("add_user_form"):
            n_name = st.text_input("Full Name")
            n_user = st.text_input("Username")
            n_role = st.selectbox("Role", ["lecturer", "admin"])
            n_pass = st.text_input("Password", type="password")
            n_confirm = st.text_input("Confirm Password", type="password")
            add_submitted = st.form_submit_button("Add User", type="primary")
        
        if add_submitted:
            if not all([n_name, n_user, n_pass]):
                st.error("All fields required.")
            elif n_pass != n_confirm:
                st.error("Passwords don't match.")
            elif n_user in users:
                st.error("Username already exists.")
            else:
                users[n_user] = {
                    "password": hash_password(n_pass),
                    "role": n_role,
                    "name": n_name,
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
                save_users(users)
                st.success(f"✅ User '{n_user}' created.")
                st.rerun()
    
    with col2:
        st.subheader("🗑️ Remove User")
        other_users = [u for u in users if u != st.session_state.username]
        if other_users:
            del_user = st.selectbox("Select user to remove", other_users)
            if st.button("🗑️ Remove User", type="secondary"):
                del users[del_user]
                save_users(users)
                st.success(f"✅ Removed user '{del_user}'")
                st.rerun()
        else:
            st.info("No other users to remove.")
        
        st.markdown("---")
        st.subheader("🔑 Change My Password")
        with st.form("change_pass_form"):
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            new_pass2 = st.text_input("Confirm New Password", type="password")
            change_submitted = st.form_submit_button("Update Password")
        
        if change_submitted:
            current_user = st.session_state.username
            if users[current_user]["password"] != hash_password(old_pass):
                st.error("Current password is incorrect.")
            elif new_pass != new_pass2:
                st.error("New passwords don't match.")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                users[current_user]["password"] = hash_password(new_pass)
                save_users(users)
                st.success("✅ Password updated successfully!")

# ─── Main Router ──────────────────────────────────────────────────────────────

def main():
    if not st.session_state.logged_in:
        show_login()
        return
    
    show_sidebar()
    
    page = st.session_state.page
    
    if page == "dashboard":
        show_dashboard()
    elif page == "mark_attendance":
        show_mark_attendance()
    elif page == "face_recognition":
        show_face_recognition()
    elif page == "students":
        show_students()
    elif page == "register_student":
        show_register_student()
    elif page == "university_integration":
        show_university_integration()
    elif page == "settings":
        show_settings()
    elif page == "reports":
        show_reports()
    elif page == "manage_users":
        if st.session_state.user_info.get("role") == "admin":
            show_manage_users()
        else:
            st.error("Access denied. Admin only.")
    else:
        st.warning("Page not found — redirected to dashboard.")
        st.session_state.page = "dashboard"
        st.experimental_rerun()

if __name__ == "__main__":
    main()
