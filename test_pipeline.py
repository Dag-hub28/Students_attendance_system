"""
Quick test to verify face recognition pipeline works
"""
import cv2
import time
import os
import numpy as np
from live_monitoring import LiveMonitoringSystem

def test_basic_recognition():
    """Test basic face recognition without camera"""
    monitor = LiveMonitoringSystem()
    
    # Check face database
    num_faces = len(monitor.known_faces_data.get('faces', []))
    print(f"Faces in database: {num_faces}")
    
    # Test with existing face images
    faces_dir = 'faces'
    test_results = []
    
    if num_faces > 0:
        for i, face_path in enumerate(monitor.known_faces_data['faces'][:3]):
            if os.path.exists(face_path):
                img = cv2.imread(face_path)
                if img is not None:
                    t0 = time.time()
                    detected = monitor.recognize_face(img)
                    elapsed = (time.time() - t0) * 1000
                    
                    test_results.append({
                        'image': face_path,
                        'detected': detected,
                        'response_ms': elapsed
                    })
                    print(f"Test {i+1}: {face_path} -> detected: {detected}, time: {elapsed:.1f}ms")
    
    return test_results

def test_embedding_extraction():
    """Test face embedding extraction"""
    monitor = LiveMonitoringSystem()
    
    # Create a simple test image
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    embedding = monitor._get_face_embedding(test_img)
    
    if embedding is not None:
        print(f"Embedding shape: {embedding.shape}, norm: {np.linalg.norm(embedding):.4f}")
        return True
    else:
        print("Embedding extraction failed")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Face Recognition Pipeline Test")
    print("=" * 50)
    
    print("\n1. Testing embedding extraction...")
    test_embedding_extraction()
    
    print("\n2. Testing recognition with stored faces...")
    results = test_basic_recognition()
    
    if results:
        avg_time = sum(r['response_ms'] for r in results) / len(results)
        print(f"\nAverage response time: {avg_time:.1f}ms")
        
        if avg_time < 3000:
            print("[OK] Response time under 3 seconds target")
        else:
            print("[WARN] Response time exceeds 3 seconds target")