"""
Continuous Presence Monitoring Module
Handles 10-minute verification intervals during class sessions.
"""
import threading
import time
from datetime import datetime
from flask import session

class ContinuousMonitor:
    """Manages periodic verification during class sessions"""
    
    def __init__(self, live_monitor):
        self.live_monitor = live_monitor
        self.active = False
        self.thread = None
        self.interval_seconds = 600  # 10 minutes
        self.verification_callbacks = []
    
    def start(self):
        """Start the continuous monitoring thread"""
        if self.active:
            return
        
        self.active = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"Continuous monitoring started at {datetime.now().isoformat()}")
    
    def stop(self):
        """Stop the monitoring thread"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Continuous monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop - checks every 10 minutes"""
        while self.active:
            time.sleep(self.interval_seconds)
            if not self.active:
                break
            
            self._perform_verification()
    
    def _perform_verification(self):
        """Perform verification checks for all monitored students"""
        present_students = self.live_monitor.get_presence_summary()['detected']
        
        for student_name in present_students:
            if self.live_monitor.verify_student_at_interval(student_name, 10):
                # Trigger verification callback
                for callback in self.verification_callbacks:
                    callback(student_name)
                
                # Update verification timestamp
                self.live_monitor.update_verification_time(student_name)
    
    def register_callback(self, callback):
        """Register a callback for verification events"""
        self.verification_callbacks.append(callback)
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'active': self.active,
            'interval_minutes': self.interval_seconds // 60,
            'next_check': datetime.now().isoformat()
        }


# Global monitor instance
continuous_monitor = None

def get_continuous_monitor(live_monitor):
    """Get or create the global monitor instance"""
    global continuous_monitor
    if continuous_monitor is None:
        continuous_monitor = ContinuousMonitor(live_monitor)
    return continuous_monitor


def init_continuous_monitoring(app, live_monitor):
    """Initialize continuous monitoring routes"""
    
    @app.route('/start_continuous_monitoring')
    def start_monitoring():
        if 'user_id' not in session or session.get('role') != 'student':
            return {'error': 'Unauthorized'}, 401
        
        monitor = get_continuous_monitor(live_monitor)
        monitor.start()
        
        return {'status': 'started', 'interval_minutes': 10}
    
    @app.route('/stop_continuous_monitoring')
    def stop_monitoring():
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        
        global continuous_monitor
        if continuous_monitor:
            continuous_monitor.stop()
        
        return {'status': 'stopped'}
    
    @app.route('/monitoring_status')
    def monitoring_status():
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        
        monitor = get_continuous_monitor(live_monitor)
        return monitor.get_status()