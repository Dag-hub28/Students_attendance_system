"""
Setup test faces for accuracy testing
Creates synthetic face images for testing the recognition system
"""
import cv2
import numpy as np
import os
from live_monitoring import LiveMonitoringSystem

def create_test_faces():
    """Create synthetic face images for testing"""
    os.makedirs('faces', exist_ok=True)
    
    monitor = LiveMonitoringSystem()
    
    # Create 5 synthetic student faces with different patterns
    names = ['student_a', 'student_b', 'student_c', 'student_d', 'student_e']
    
    for name in names:
        # Create synthetic face pattern (simple colored circles to simulate faces)
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        
        # Add face-like pattern
        cv2.circle(img, (100, 90), 50, (200, 180, 160), -1)  # Face
        cv2.circle(img, (80, 80), 10, (50, 50, 50), -1)  # Left eye
        cv2.circle(img, (120, 80), 10, (50, 50, 50), -1)  # Right eye
        cv2.ellipse(img, (100, 110), (20, 10), 0, 0, 180, (100, 100, 100), -1)  # Smile
        
        # Add unique color pattern for each student
        color_offset = (hash(name) % 100)
        img[:,:,0] = np.clip(img[:,:,0] + color_offset, 0, 255)
        
        # Save as enrolled face
        monitor.add_known_face(name, img, sample_type='primary')
        print(f"Created test face for {name}")
        
        # Create additional samples with variations
        img2 = img.copy()
        img2 = cv2.convertScaleAbs(img2, alpha=0.8, beta=20)  # Dimmer
        monitor.add_known_face(name, img2, sample_type='dim_light')
        print(f"Created dim light sample for {name}")
    
    print(f"\nTotal faces enrolled: {len(monitor.known_faces_data['faces'])}")
    return monitor

def test_with_enrolled_faces(monitor):
    """Test recognition with freshly enrolled synthetic faces"""
    import time
    
    results = []
    for name in ['student_a', 'student_b', 'student_c', 'student_d', 'student_e']:
        # Create test image similar to enrolled
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        cv2.circle(img, (100, 90), 50, (200, 180, 160), -1)
        cv2.circle(img, (80, 80), 10, (50, 50, 50), -1)
        cv2.circle(img, (120, 80), 10, (50, 50, 50), -1)
        cv2.ellipse(img, (100, 110), (20, 10), 0, 0, 180, (100, 100, 100), -1)
        
        color_offset = (hash(name) % 100)
        img[:,:,0] = np.clip(img[:,:,0] + color_offset, 0, 255)
        
        t0 = time.time()
        detected = monitor.recognize_face(img)
        elapsed = (time.time() - t0) * 1000
        
        results.append({
            'expected': name,
            'detected': detected,
            'correct': name in detected,
            'time_ms': elapsed
        })
        print(f"Expected: {name}, Detected: {detected}, Correct: {name in detected}, Time: {elapsed:.1f}ms")
    
    accuracy = sum(1 for r in results if r['correct']) / len(results) * 100
    avg_time = sum(r['time_ms'] for r in results) / len(results)
    
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.1f}%")
    print(f"  Average time: {avg_time:.1f}ms")
    
    return results

if __name__ == '__main__':
    print("Setting up test faces...")
    monitor = create_test_faces()
    
    print("\nTesting recognition...")
    test_with_enrolled_faces(monitor)