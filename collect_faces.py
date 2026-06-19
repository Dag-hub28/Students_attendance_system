"""
Quick face data collection script for testing.
Run this to rapidly collect multiple face samples for accuracy testing.
"""
import cv2
import os
from datetime import datetime
from live_monitoring import LiveMonitoringSystem

def collect_multiple_samples(name, num_samples=5):
    """Collect multiple face samples quickly for testing"""
    cap = cv2.VideoCapture(0)
    monitor = LiveMonitoringSystem()
    
    samples_collected = 0
    
    # Prepare output directory for saved samples
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('collected_faces', f"{name}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Collecting {num_samples} samples for {name}")
    print(f"Samples will be saved to: {out_dir}")
    print("Position face in frame. Press SPACE to capture, Q to quit")
    
    while samples_collected < num_samples:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Show preview
        cv2.putText(frame, f"Samples: {samples_collected}/{num_samples}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: Capture, Q: Quit", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Face Collection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # Space to capture (32 == ord(' '))
            ret2, frame2 = cap.read()
            if ret2:
                # Save image to disk
                filename = os.path.join(out_dir, f"{name}_sample_{samples_collected+1}.jpg")
                cv2.imwrite(filename, frame2)
                # Register with monitoring system (in-memory / DB as implemented)
                monitor.add_known_face(name, frame2, f'sample_{samples_collected+1}')
                samples_collected += 1
                print(f"Captured sample {samples_collected} -> {filename}")
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Done! Collected {samples_collected} samples for {name}")

if __name__ == '__main__':
    name = input("Enter the name for face samples: ").strip()
    if not name:
        name = "test_user"
    
    num = input("Number of samples to collect (default 5): ").strip()
    num = int(num) if num.isdigit() else 5
    
    collect_multiple_samples(name, num)