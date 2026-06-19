import cv2
import numpy as np
import pickle
import os
from datetime import datetime
import csv
from deepface import DeepFace
from mtcnn import MTCNN
import threading

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
FACES_DIR = os.path.join(DATA_DIR, 'faces')
ATTENDANCE_DIR = os.path.join(DATA_DIR, 'attendance')
FACE_DB_FILE = os.path.join(DATA_DIR, 'face_database.pkl')
TEMP_FACE_FILE = os.path.join(DATA_DIR, 'temp_face.jpg')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

class SimpleAttendanceSystem:
    def __init__(self):
        self.known_faces = []
        self.known_names = []
        self.attendance_logged = set()
        self.detector = MTCNN()  # Face detector
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load or create known face database"""
        if os.path.exists(FACE_DB_FILE):
            try:
                with open(FACE_DB_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces = data['faces']
                    self.known_names = data['names']
                print(f"✅ Loaded {len(self.known_names)} known faces")
            except Exception:
                print("⚠️  Could not load database. Creating new one.")
                self.known_faces = []
                self.known_names = []
        else:
            print("📝 No existing faces found. Let's register students!")
            self.register_students()
    
    def register_students(self):
        """Register new students using webcam"""
        print("\n=== STUDENT REGISTRATION ===")
        print("Press 'SPACE' to capture face")
        print("Press 'q' to quit registration")
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            faces = self.detector.detect_faces(frame)
            
            # Draw rectangles around detected faces
            for face in faces:
                x, y, w, h = face['box']
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Instructions
            cv2.putText(frame, "Press SPACE to capture, q to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Registered: {len(self.known_names)}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            cv2.imshow('Register Students', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(faces) > 0:  # Space key
                # Get the largest face
                largest_face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
                x, y, w, h = largest_face['box']
                
                # Extract face
                face_img = frame[y:y+h, x:x+w]
                
                # Get student name
                name = input("\nEnter student name: ").strip()
                
                # Save face image
                os.makedirs(FACES_DIR, exist_ok=True)
                face_filename = os.path.join(FACES_DIR, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(face_filename, face_img)
                
                # Store in database
                self.known_faces.append(face_filename)
                self.known_names.append(name)
                
                print(f"✅ Student {name} registered!")
                
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save database
        if self.known_names:
            data = {'faces': self.known_faces, 'names': self.known_names}
            with open(FACE_DB_FILE, 'wb') as f:
                pickle.dump(data, f)
            print(f"\n✅ Saved {len(self.known_names)} students to database!")
    
    def recognize_face(self, face_img):
        """Recognize a face using DeepFace"""
        if len(self.known_faces) == 0:
            return "Unknown", 0
        
        try:
            # Save temporary face
            temp_path = TEMP_FACE_FILE
            cv2.imwrite(temp_path, face_img)
            
            # Compare with known faces
            for known_path, name in zip(self.known_faces, self.known_names):
                try:
                    result = DeepFace.verify(temp_path, known_path, enforce_detection=False)
                    if result['verified']:
                        os.remove(temp_path)
                        return name, result['distance']
                except:
                    continue
            
            os.remove(temp_path)
            return "Unknown", 1.0
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown", 1.0
    
    def mark_attendance(self, name):
        """Mark attendance in CSV"""
        if name in self.attendance_logged:
            return False
        
        filename = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
        os.makedirs(ATTENDANCE_DIR, exist_ok=True)
        current_time = datetime.now().strftime('%H:%M:%S')
        
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Name', 'Time', 'Date', 'Confidence'])
            writer.writerow([name, current_time, datetime.now().strftime('%Y-%m-%d'), "High"])
        
        self.attendance_logged.add(name)
        return True
    
    def run(self):
        """Main attendance loop"""
        print("\n=== ATTENDANCE SYSTEM RUNNING ===")
        print("Press 'q' to quit")
        print("Press 'r' to register more students")
        
        cap = cv2.VideoCapture(0)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect faces
            faces = self.detector.detect_faces(frame)
            
            # Process each face
            for face in faces:
                x, y, w, h = face['box']
                # Ensure coordinates are within frame
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1]-x), min(h, frame.shape[0]-y)
                
                # Extract face
                face_img = frame[y:y+h, x:x+w]
                
                # Recognize face (every 10 frames to save processing)
                if frame_count % 10 == 0 and face_img.size > 0:
                    name, confidence = self.recognize_face(face_img)
                    
                    # Draw rectangle and name
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Add name and confidence
                    label = f"{name}"
                    if name != "Unknown":
                        label += f" ({1-confidence:.2f})"
                    
                    cv2.putText(frame, label, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Mark attendance
                    if name != "Unknown":
                        if self.mark_attendance(name):
                            print(f"✅ Attendance marked: {name}")
            
            # Display info
            cv2.putText(frame, f"Present: {len(self.attendance_logged)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "q: quit | r: register", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Attendance System', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                cap.release()
                cv2.destroyAllWindows()
                self.register_students()
                # Restart
                self.attendance_logged.clear()
                return self.run()
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n=== SUMMARY ===")
        print(f"Total marked: {len(self.attendance_logged)}")

if __name__ == "__main__":
    print("=" * 50)
    print("AI ATTENDANCE SYSTEM")
    print("=" * 50)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FACES_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    
    system = SimpleAttendanceSystem()
    system.run()