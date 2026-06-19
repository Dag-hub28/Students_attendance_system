"""
Face Recognition Accuracy Testing Script
Collects accuracy metrics for the AI facial recognition system.
"""
import cv2
import time
import json
import os
from datetime import datetime
from live_monitoring import LiveMonitoringSystem

def benchmark_recognition(video_source=0, num_tests=100):
    """Benchmark recognition performance with timing metrics"""
    monitor = LiveMonitoringSystem()
    
    # Load known faces if available
    num_known = len(monitor.known_faces_data.get('names', []))
    print(f"Known faces in database: {num_known}")
    
    if num_known == 0:
        print("No faces enrolled. Please enroll faces first.")
        return
    
    cap = cv2.VideoCapture(video_source)
    metrics = {
        'total_frames': 0,
        'detected_frames': 0,
        'total_time': 0,
        'avg_response_ms': 0,
        'min_response_ms': float('inf'),
        'max_response_ms': 0,
        'accuracy_by_name': {}
    }
    
    print(f"Running {num_tests} recognition tests...")
    
    for i in range(num_tests):
        ret, frame = cap.read()
        if not ret:
            break
            
        t0 = time.time()
        detected = monitor.recognize_face(frame)
        t1 = time.time()
        
        elapsed_ms = (t1 - t0) * 1000
        
        if detected:
            metrics['detected_frames'] += 1
            for name in detected:
                if name not in metrics['accuracy_by_name']:
                    metrics['accuracy_by_name'][name] = {'detected': 0, 'total': 0}
                metrics['accuracy_by_name'][name]['detected'] += 1
        
        metrics['total_frames'] += 1
        metrics['total_time'] += elapsed_ms
        metrics['min_response_ms'] = min(metrics['min_response_ms'], elapsed_ms)
        metrics['max_response_ms'] = max(metrics['max_response_ms'], elapsed_ms)
        
        # Show progress
        if (i + 1) % 10 == 0:
            print(f"Progress: {i+1}/{num_tests} frames")
    
    cap.release()
    
    if metrics['total_frames'] > 0:
        metrics['avg_response_ms'] = metrics['total_time'] / metrics['total_frames']
    
    return metrics

def collect_volunteer_samples(output_dir='volunteer_dataset', num_samples=3):
    """Collect face samples from volunteers under different conditions"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("Volunteer Face Collection Tool")
    print("=" * 40)
    
    name = input("Enter volunteer name (or 'quit' to exit): ").strip()
    if name.lower() == 'quit':
        return
    
    cap = cv2.VideoCapture(0)
    conditions = ['primary', 'dim_light', 'backlit', 'profile_angle']
    
    collected = 0
    for condition in conditions[:num_samples]:
        print(f"\nCondition: {condition}")
        print("Position yourself appropriately...")
        input("Press Enter when ready...")
        
        ret, frame = cap.read()
        if ret:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{output_dir}/{name}_{condition}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            collected += 1
    
    cap.release()
    print(f"\nCollected {collected} samples for {name}")

def run_live_test(duration_seconds=60):
    """Run live recognition test with visualization"""
    monitor = LiveMonitoringSystem()
    cap = cv2.VideoCapture(0)
    
    results = []
    start_time = time.time()
    
    print(f"Running live test for {duration_seconds} seconds...")
    
    while time.time() - start_time < duration_seconds:
        ret, frame = cap.read()
        if not ret:
            break
        
        t0 = time.time()
        detected = monitor.recognize_face(frame)
        elapsed = (time.time() - t0) * 1000
        
        results.append({
            'timestamp': time.time(),
            'detected': detected,
            'response_ms': elapsed
        })
        
        # Visualize
        for name in detected:
            cv2.putText(frame, f"Detected: {name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Response: {elapsed:.1f}ms", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Accuracy Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'accuracy_results_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    avg_response = sum(r['response_ms'] for r in results) / len(results) if results else 0
    detection_rate = len([r for r in results if r['detected']]) / len(results) * 100 if results else 0
    
    print(f"\nResults:")
    print(f"  Average response: {avg_response:.1f}ms")
    print(f"  Detection rate: {detection_rate:.1f}%")
    print(f"  Results saved: accuracy_results_{timestamp}.json")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'benchmark':
            metrics = benchmark_recognition(num_tests=int(sys.argv[2]) if len(sys.argv) > 2 else 100)
            if metrics:
                print(f"\nBenchmark Results:")
                print(f"  Frames processed: {metrics['total_frames']}")
                print(f"  Detection rate: {metrics['detected_frames']/metrics['total_frames']*100:.1f}%")
                print(f"  Avg response: {metrics['avg_response_ms']:.1f}ms")
                print(f"  Min/Max: {metrics['min_response_ms']:.1f}ms / {metrics['max_response_ms']:.1f}ms")
        
        elif command == 'volunteer':
            collect_volunteer_samples()
        
        elif command == 'live':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            run_live_test(duration)
        
        else:
            print("Usage: python test_accuracy.py [benchmark|volunteer|live]")
    else:
        print("Face Recognition Accuracy Tester")
        print("Commands:")
        print("  benchmark [n] - Run n recognition tests")
        print("  volunteer     - Collect volunteer face samples")
        print("  live [sec]    - Run live test for n seconds")