import sys
import cv2
import numpy as np
import pickle
import os
from datetime import datetime
import csv
from deepface import DeepFace
from mtcnn import MTCNN
import threading
import time

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
FACES_DIR = os.path.join(DATA_DIR, 'faces')
ATTENDANCE_DIR = os.path.join(DATA_DIR, 'attendance')
FACE_DB_FILE = os.path.join(DATA_DIR, 'face_database.pkl')
TEMP_FACE_FILE = os.path.join(DATA_DIR, 'temp_face.jpg')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# Ensure UTF-8 for print/log output to avoid charmap errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

class SimpleAttendanceSystem:
    def __init__(self):
        self.known_faces = []
        self.known_names = []
        self.attendance_logged = set()
        self.detector = MTCNN()
        self.load_known_faces()
        self.recognition_cache = {}  # Cache recent recognitions
        self.last_recognition_time = {}
        
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
        print("\n" + "="*50)
        print("STUDENT REGISTRATION MODE")
        print("="*50)
        print("📸 Instructions:")
        print("   - Look directly at the camera")
        print("   - Press SPACEBAR to capture your face")
        print("   - Type your name in the terminal")
        print("   - Press 'q' when done registering")
        print("="*50)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        # Create faces directory if it doesn't exist
        os.makedirs(FACES_DIR, exist_ok=True)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read from camera")
                break
            
            # Detect faces
            try:
                faces = self.detector.detect_faces(frame)
            except:
                faces = []
            
            # Draw rectangles around detected faces
            for face in faces:
                x, y, w, h = face['box']
                # Ensure coordinates are within frame
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1]-x), min(h, frame.shape[0]-y)
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Instructions overlay
            cv2.putText(frame, f"Registered: {len(self.known_names)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "SPACE: Capture | q: Quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Register Students', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(faces) > 0:  # Space key
                # Get the largest face
                largest_face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
                x, y, w, h = largest_face['box']
                
                # Ensure coordinates are valid
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1]-x), min(h, frame.shape[0]-y)
                
                # Extract face
                face_img = frame[y:y+h, x:x+w]
                
                if face_img.size > 0:
                    # Get student name
                    name = input("\n📝 Enter student name: ").strip()
                    
                    if name:
                        # Save face image
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        face_filename = os.path.join(FACES_DIR, f"{name}_{timestamp}.jpg")
                        cv2.imwrite(face_filename, face_img)
                        
                        # Store in database
                        self.known_faces.append(face_filename)
                        self.known_names.append(name)
                        
                        print(f"✅ Student {name} registered successfully!")
                        
                        # Show success on screen
                        cv2.putText(frame, "REGISTERED!", (50, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        cv2.imshow('Register Students', frame)
                        cv2.waitKey(1000)
            
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
            print(f"📁 Faces saved in '{FACES_DIR}' folder")
        else:
            print("⚠️  No students registered")
    
    def recognize_face(self, face_img, face_location):
        """Recognize a face using DeepFace with caching"""
        if len(self.known_faces) == 0:
            return "Unknown", 1.0
        
        # Create a simple hash for caching based on face location
        location_hash = f"{face_location[0]}_{face_location[1]}"
        
        # Check cache (avoid processing same face too often)
        current_time = time.time()
        if location_hash in self.last_recognition_time:
            if current_time - self.last_recognition_time[location_hash] < 2:  # 2 second cache
                return self.recognition_cache.get(location_hash, ("Unknown", 1.0))
        
        try:
            # Save temporary face
            temp_path = "temp_face.jpg"
            cv2.imwrite(temp_path, face_img)
            
            best_match = "Unknown"
            best_distance = 1.0
            
            # Compare with known faces
            for known_path, name in zip(self.known_faces, self.known_names):
                try:
                    # Verify with DeepFace
                    result = DeepFace.verify(temp_path, known_path, 
                                           enforce_detection=False,
                                           model_name='Facenet',
                                           distance_metric='cosine')
                    
                    if result['verified']:
                        best_match = name
                        best_distance = result['distance']
                        break
                except Exception as e:
                    continue
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Update cache
            self.recognition_cache[location_hash] = (best_match, best_distance)
            self.last_recognition_time[location_hash] = current_time
            
            return best_match, best_distance
            
        except Exception as e:
            return "Unknown", 1.0
    
    def mark_attendance(self, name):
        """Mark attendance in CSV"""
        if name in self.attendance_logged:
            return False
        
        # Create filename with current date
        filename = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
        os.makedirs(ATTENDANCE_DIR, exist_ok=True)
        current_time = datetime.now().strftime('%H:%M:%S')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Name', 'Time', 'Date', 'Status'])
            writer.writerow([name, current_time, current_date, 'Present'])
        
        self.attendance_logged.add(name)
        return True
    
    def run(self):
        """Main attendance loop"""
        print("\n" + "="*50)
        print("ATTENDANCE SYSTEM RUNNING")
        print("="*50)
        print("🎯 Commands:")
        print("   - 'q': Quit system")
        print("   - 'r': Register more students")
        print("   - 'c': Clear today's attendance")
        print("="*50)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        frame_count = 0
        fps_start_time = time.time()
        fps = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read from camera")
                break
            
            frame_count += 1
            
            # Calculate FPS
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                time_diff = fps_end_time - fps_start_time
                fps = 30 / time_diff if time_diff > 0 else 0
                fps_start_time = fps_end_time
            
            # Detect faces every frame for display, but recognize every 10 frames for speed
            try:
                faces = self.detector.detect_faces(frame)
            except:
                faces = []
            
            # Process each face
            for face in faces:
                x, y, w, h = face['box']
                # Ensure coordinates are within frame
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1]-x), min(h, frame.shape[0]-y)
                
                # Extract face
                face_img = frame[y:y+h, x:x+w]
                
                # Default color and label
                color = (0, 0, 255)  # Red for unknown
                label = "Unknown"
                
                # Recognize face (every 5 frames to save processing)
                if face_img.size > 0:
                    if frame_count % 5 == 0:
                        name, confidence = self.recognize_face(face_img, (x, y))
                        
                        if name != "Unknown":
                            color = (0, 255, 0)  # Green for known
                            confidence_score = 1 - confidence
                            label = f"{name} ({confidence_score:.2f})"
                            
                            # Mark attendance
                            if self.mark_attendance(name):
                                print(f"✅ {name} marked present at {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            label = "Unknown"
                    
                    # Use cached result if available
                    elif (x, y) in self.recognition_cache:
                        cached_name, cached_conf = self.recognition_cache.get((x, y), ("Unknown", 1.0))
                        if cached_name != "Unknown":
                            color = (0, 255, 0)
                            label = f"{cached_name}"
                
                # Draw bounding box and label
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x, y-25), (x + label_size[0], y), color, -1)
                
                # Draw label text
                cv2.putText(frame, label, (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display info overlay
            cv2.putText(frame, f"Present: {len(self.attendance_logged)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, "q:quit | r:register | c:clear", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('AI Attendance System', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                cap.release()
                cv2.destroyAllWindows()
                self.register_students()
                # Restart attendance
                print("\n🔄 Restarting attendance system...")
                self.attendance_logged.clear()
                return self.run()
            elif key == ord('c'):
                self.attendance_logged.clear()
                print("🧹 Cleared today's attendance")
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "="*50)
        print("SESSION SUMMARY")
        print("="*50)
        print(f"📊 Total students marked: {len(self.attendance_logged)}")
        
        # Show attendance file location
        filename = os.path.join(ATTENDANCE_DIR, f"attendance_{datetime.now().strftime('%Y%m%d')}.csv")
        if os.path.exists(filename):
            print(f"📁 Attendance saved to: {filename}")
            
            # Preview attendance
            print("\n📋 Today's Attendance:")
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    print(f"   • {row[0]} - {row[1]}")
        print("="*50)

def main():
    print("\n" + "="*60)
    print("     AI-POWERED ATTENDANCE VERIFICATION SYSTEM")
    print("="*60)
    print("⚡ Initializing system...")
    
    # Create necessary directories
    os.makedirs(FACES_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    
    # Create and run the system
    try:
        system = SimpleAttendanceSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Thank you for using the Attendance System!")

if __name__ == "__main__":
    main()