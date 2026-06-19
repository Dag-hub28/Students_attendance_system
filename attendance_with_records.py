import csv
import os
from datetime import datetime
import pickle
import time

class AttendanceSystem:
    def __init__(self):
        self.students = []
        self.attendance_logged = set()
        self.engagement_scores = {}
        self.load_data()
        
    def load_data(self):
        """Load student data"""
        if os.path.exists('students.pkl'):
            try:
                with open('students.pkl', 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.students = data.get('students', [])
                        self.engagement_scores = data.get('scores', {})
                    elif isinstance(data, list):
                        self.students = data
                        for student in self.students:
                            self.engagement_scores[student] = 100.0
                print(f"✅ Loaded {len(self.students)} students")
                self.show_today_attendance()  # Show today's attendance on startup
            except Exception as e:
                print(f"⚠️ Error loading data: {e}")
                self.students = []
                self.engagement_scores = {}
        else:
            print("📝 No students found. Let's register!")
            self.register_students()
    
    def save_data(self):
        """Save student data"""
        data = {
            'students': self.students,
            'scores': self.engagement_scores
        }
        with open('students.pkl', 'wb') as f:
            pickle.dump(data, f)
    
    def show_today_attendance(self):
        """Show today's attendance records"""
        filename = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        if os.path.exists(filename):
            print(f"\n📋 Today's Attendance Records:")
            print("-" * 50)
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Skip headers
                for row in reader:
                    print(f"  {row[0]}: {row[1]} - Score: {row[3]}")
            print("-" * 50)
            print(f"✅ Total: {len(self.attendance_logged)} students present")
        else:
            print("\n📋 No attendance records for today yet.")
    
    def register_students(self):
        """Register students manually"""
        print("\n" + "="*50)
        print("📝 STUDENT REGISTRATION")
        print("="*50)
        print("Enter student names (one per line)")
        print("Type 'done' when finished")
        print("="*50)
        
        count = 0
        while True:
            name = input(f"Student #{count+1}: ").strip()
            if name.lower() == 'done':
                break
            if name:
                if name not in self.students:
                    self.students.append(name)
                    self.engagement_scores[name] = 100.0
                    count += 1
                    print(f"✅ Added {name} (Total: {count})")
                else:
                    print(f"⚠️ {name} already exists")
        
        if self.students:
            self.save_data()
            print(f"\n✅ Successfully registered {count} new students!")
            print(f"📋 Total students now: {len(self.students)}")
    
    def mark_attendance(self, name):
        """Mark attendance with visible confirmation"""
        if name in self.attendance_logged:
            print(f"⚠️ {name} was already marked at {self.get_attendance_time(name)}")
            return False
        
        filename = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        current_time = datetime.now().strftime('%H:%M:%S')
        current_date = datetime.now().strftime('%Y-%m-%d')
        score = self.engagement_scores.get(name, 100.0)
        
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Name', 'Time', 'Date', 'Engagement Score'])
            writer.writerow([name, current_time, current_date, f"{score:.1f}%"])
        
        self.attendance_logged.add(name)
        
        # Show clear confirmation
        print("\n" + "="*50)
        print(f"✅ ATTENDANCE RECORDED!")
        print("="*50)
        print(f"Student: {name}")
        print(f"Time: {current_time}")
        print(f"Date: {current_date}")
        print(f"Score: {score:.1f}%")
        print("="*50)
        
        # Show updated totals
        print(f"📊 Present today: {len(self.attendance_logged)}/{len(self.students)}")
        return True
    
    def get_attendance_time(self, name):
        """Get the time a student was marked"""
        filename = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row[0] == name:
                        return row[1]
        return "unknown time"
    
    def mark_all_attendance(self):
        """Mark all students present"""
        print("\n" + "="*50)
        print("📝 MARKING ALL STUDENTS PRESENT")
        print("="*50)
        
        count = 0
        for student in self.students:
            if student not in self.attendance_logged:
                self.mark_attendance(student)
                count += 1
                time.sleep(0.5)  # Pause so you can see each one
        
        print(f"\n✅ Marked {count} students present")
        print(f"📊 Total present: {len(self.attendance_logged)}/{len(self.students)}")
    
    def update_score(self, name, change):
        """Update engagement score with confirmation"""
        if name in self.engagement_scores:
            old_score = self.engagement_scores[name]
            new_score = max(0, min(100, old_score + change))
            self.engagement_scores[name] = new_score
            
            # Show clear update
            print("\n" + "-"*40)
            if change > 0:
                print(f"👍 ENGAGEMENT INCREASED!")
            else:
                print(f"👎 ENGAGEMENT DECREASED!")
            print("-"*40)
            print(f"Student: {name}")
            print(f"Change: {change:+.1f}%")
            print(f"Score: {old_score:.1f}% → {new_score:.1f}%")
            print("-"*40)
            
            self.save_data()
        else:
            print(f"❌ Student {name} not found")
    
    def show_students(self):
        """Display all students with clear formatting"""
        print("\n" + "="*60)
        print(f"📋 STUDENT LIST - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        if not self.students:
            print("⚠️ No students registered yet. Type 'r' to register.")
            return
        
        # Calculate statistics
        present_count = len(self.attendance_logged)
        avg_score = sum(self.engagement_scores.values()) / len(self.engagement_scores) if self.engagement_scores else 0
        
        print(f"Total Students: {len(self.students)} | Present: {present_count} | Avg Score: {avg_score:.1f}%")
        print("-" * 60)
        
        for i, student in enumerate(self.students, 1):
            score = self.engagement_scores.get(student, 100.0)
            status = "✓" if student in self.attendance_logged else "○"
            
            # Choose emoji based on score
            if score >= 90:
                emoji = "🌟"
            elif score >= 75:
                emoji = "👍"
            elif score >= 60:
                emoji = "👌"
            elif score >= 40:
                emoji = "⚠️"
            else:
                emoji = "🔴"
            
            # Show attendance time if present
            if student in self.attendance_logged:
                time_str = f" at {self.get_attendance_time(student)}"
            else:
                time_str = ""
            
            print(f"{i:2}. {emoji} {student:15} - {score:5.1f}% [{status}]{time_str}")
        
        print("="*60)
    
    def show_attendance_report(self):
        """Show detailed attendance report"""
        filename = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        
        print("\n" + "="*60)
        print("📊 ATTENDANCE REPORT")
        print("="*60)
        
        if not os.path.exists(filename):
            print("❌ No attendance recorded today yet.")
            return
        
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if len(rows) <= 1:
                print("❌ No attendance records found.")
                return
            
            headers = rows[0]
            records = rows[1:]
            
            print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"Total Records: {len(records)}")
            print("-" * 60)
            
            for row in records:
                print(f"  {row[0]:15} - {row[1]} - Score: {row[3]}")
            
            print("-" * 60)
            print(f"✅ File saved as: {filename}")
    
    def student_menu(self, name):
        """Menu for individual student"""
        while True:
            score = self.engagement_scores.get(name, 100.0)
            status = "✓ Present" if name in self.attendance_logged else "○ Absent"
            time_str = f" at {self.get_attendance_time(name)}" if name in self.attendance_logged else ""
            
            print("\n" + "="*50)
            print(f"   👤 STUDENT: {name}")
            print("="*50)
            print(f"Current Score: {score:.1f}%")
            print(f"Status: {status}{time_str}")
            print("\n📋 ACTIONS:")
            print("  1 - Good engagement (+5%)")
            print("  2 - Low engagement (-5%)")
            print("  3 - Very low engagement (-10%)")
            print("  a - Mark attendance")
            print("  r - View attendance record")
            print("  b - Back to main menu")
            print("="*50)
            
            choice = input("📝 Choice: ").strip().lower()
            
            if choice == '1':
                self.update_score(name, 5)
            elif choice == '2':
                self.update_score(name, -5)
            elif choice == '3':
                self.update_score(name, -10)
            elif choice == 'a':
                self.mark_attendance(name)
            elif choice == 'r':
                self.show_student_record(name)
            elif choice == 'b':
                break
            else:
                print("❌ Invalid choice")
    
    def show_student_record(self, name):
        """Show individual student's attendance record"""
        print(f"\n📋 Attendance history for {name}:")
        print("-" * 40)
        
        # Check today's file
        filename = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                found = False
                for row in reader:
                    if row[0] == name:
                        print(f"  Today: {row[1]} - Score: {row[3]}")
                        found = True
                if not found:
                    print("  No record for today")
        
        # Check previous days
        print("\n  Previous days:")
        for file in os.listdir('.'):
            if file.startswith('attendance_') and file != filename:
                date = file.replace('attendance_', '').replace('.csv', '')
                with open(file, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        if row[0] == name:
                            print(f"  {date[:4]}-{date[4:6]}-{date[6:8]}: {row[1]} - Score: {row[3]}")
        print("-" * 40)
    
    def show_help(self):
        """Show help menu"""
        print("\n" + "="*50)
        print("📖 HELP - COMMANDS")
        print("="*50)
        print("Main Menu:")
        print("  [number] - Select student")
        print("  a - Mark ALL students present")
        print("  r - Register new student(s)")
        print("  l - List all students")
        print("  s - Show engagement summary")
        print("  v - View today's attendance report")
        print("  h - Show this help")
        print("  q - Quit and show final report")
        print("\nStudent Menu:")
        print("  1 - Good engagement (+5%)")
        print("  2 - Low engagement (-5%)")
        print("  3 - Very low (-10%)")
        print("  a - Mark attendance")
        print("  r - View attendance record")
        print("  b - Back")
        print("="*50)
    
    def run(self):
        """Main system"""
        print("\n" + "="*60)
        print("   🎓 ATTENDANCE TRACKING SYSTEM")
        print("="*60)
        print("Type 'h' for help")
        print("="*60)
        
        while True:
            self.show_students()
            
            cmd = input("\n📝 Command: ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'a':
                self.mark_all_attendance()
            elif cmd == 'r':
                self.register_students()
            elif cmd == 'l':
                self.show_students()
            elif cmd == 's':
                self.show_summary()
            elif cmd == 'v':
                self.show_attendance_report()
            elif cmd == 'h':
                self.show_help()
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(self.students):
                    self.student_menu(self.students[idx])
                else:
                    print(f"❌ Invalid number. Please enter 1-{len(self.students)}")
            elif cmd:
                print("❌ Invalid command. Type 'h' for help")
        
        self.show_final_report()
    
    def show_summary(self):
        """Show engagement summary"""
        print("\n" + "="*50)
        print("📊 ENGAGEMENT SUMMARY")
        print("="*50)
        
        if not self.students:
            print("No students registered.")
            return
        
        # Sort by score
        sorted_students = sorted(self.students, 
                                key=lambda s: self.engagement_scores.get(s, 0), 
                                reverse=True)
        
        total_score = 0
        present_count = 0
        
        for student in sorted_students:
            score = self.engagement_scores.get(student, 100.0)
            status = "Present" if student in self.attendance_logged else "Absent"
            
            if status == "Present":
                total_score += score
                present_count += 1
            
            # Rating
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
            
            print(f"\n{student}:")
            print(f"  Score: {score:.1f}% - {rating}")
            print(f"  Status: {status}")
        
        if present_count > 0:
            avg_score = total_score / present_count
            print(f"\n📊 Average Engagement: {avg_score:.1f}%")
        
        print("="*50)
    
    def show_final_report(self):
        """Show final report"""
        print("\n" + "="*60)
        print("📊 FINAL SESSION REPORT")
        print("="*60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Total Students: {len(self.students)}")
        print(f"Students Present: {len(self.attendance_logged)}")
        
        if self.attendance_logged:
            print("\n📈 ENGAGEMENT DETAILS:")
            total_score = 0
            
            for student in self.attendance_logged:
                score = self.engagement_scores.get(student, 100.0)
                total_score += score
                time_str = self.get_attendance_time(student)
                
                if score >= 90:
                    print(f"  🌟 {student}: {score:.1f}% at {time_str}")
                elif score >= 75:
                    print(f"  👍 {student}: {score:.1f}% at {time_str}")
                elif score >= 60:
                    print(f"  👌 {student}: {score:.1f}% at {time_str}")
                else:
                    print(f"  ⚠️ {student}: {score:.1f}% at {time_str}")
            
            avg_score = total_score / len(self.attendance_logged)
            print(f"\n📊 Average Engagement: {avg_score:.1f}%")
        
        self.show_attendance_report()
        print("="*60)
        print("👋 Thank you for using the system!")

def main():
    print("\n" + "="*60)
    print("   🎓 ATTENDANCE TRACKING SYSTEM")
    print("="*60)
    
    try:
        system = AttendanceSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()