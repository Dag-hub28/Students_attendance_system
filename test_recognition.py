"""
Test recognition with existing face images - loads enrolled images back and tests
"""
import cv2
import time
import numpy as np
from live_monitoring import LiveMonitoringSystem

def test_recognition_with_existing():
    """Test by loading back stored face images"""
    monitor = LiveMonitoringSystem()
    
    # Get all enrolled faces
    faces_data = monitor.known_faces_data
    print(f"Loaded {len(faces_data['faces'])} face samples for {len(set(faces_data['names']))} students")
    
    if len(faces_data['faces']) == 0:
        print("No faces enrolled. Please enroll faces first.")
        return
    
    # Test recognition by loading each stored face and checking if recognized
    results_by_student = {}
    
    for i, face_path in enumerate(faces_data['faces']):
        name = faces_data['names'][i]
        
        img = cv2.imread(face_path)
        if img is None:
            continue
        
        t0 = time.time()
        detected = monitor.recognize_face(img)
        elapsed = (time.time() - t0) * 1000
        
        if name not in results_by_student:
            results_by_student[name] = {'detected': 0, 'total': 0, 'times': []}
        
        results_by_student[name]['total'] += 1
        results_by_student[name]['times'].append(elapsed)
        
        if name in detected:
            results_by_student[name]['detected'] += 1
        
        print(f"Test {i+1}: {name} -> detected: {detected}, time: {elapsed:.1f}ms")
    
    # Calculate accuracy per student
    print("\nAccuracy by Student:")
    total_accuracy = 0
    total_tests = 0
    
    for name, stats in results_by_student.items():
        acc = stats['detected'] / stats['total'] * 100 if stats['total'] > 0 else 0
        avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
        print(f"  {name}: {stats['detected']}/{stats['total']} ({acc:.0f}%) avg time: {avg_time:.1f}ms")
        total_accuracy += stats['detected']
        total_tests += stats['total']
    
    if total_tests > 0:
        overall_acc = total_accuracy / total_tests * 100
        print(f"\nOverall: {total_accuracy}/{total_tests} ({overall_acc:.0f}%)")
        
        # Check targets
        if avg_time < 3000:
            print("[OK] Average response time under 3 seconds")
        if overall_acc >= 90:
            print("[OK] Accuracy meets 90% target")
        else:
            print("[NEEDS WORK] Accuracy below 90% target - need more training data or better model")

if __name__ == '__main__':
    print("=" * 50)
    print("Recognition Test with Existing Enrolled Faces")
    print("=" * 50 + "\n")
    test_recognition_with_existing()