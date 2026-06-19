import cv2
import pickle
import os
from datetime import datetime
import numpy as np
from collections import defaultdict, Counter, deque
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

try:
    from deepface import DeepFace
    try:
        import tensorflow as tf  # noqa: F401
        DEEPFACE_AVAILABLE = True
    except Exception:
        DEEPFACE_AVAILABLE = False
except ImportError:
    DEEPFACE_AVAILABLE = False

class PrivacyEncryption:
    """AES-256 encryption for face data"""
    
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> tuple:
        if salt is None:
            salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        return key, salt
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> bytes:
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded = plaintext + b'\x00' * (16 - len(plaintext) % 16)
        return iv + encryptor.update(padded) + encryptor.finalize()
    
    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes) -> bytes:
        iv = ciphertext[:16]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext[16:]) + decryptor.finalize()


class LiveMonitoringSystem:
    def __init__(self):
        self.known_faces_data = None
        self.cascade = None
        self.presence_log = defaultdict(lambda: {'first_seen': None, 'last_seen': None, 'count': 0, 'last_verified': None})
        self.verification_intervals = {}
        self.alerts = deque(maxlen=50)
        self.verification_history = defaultdict(list)
        self._init_detector()
        self.load_known_faces()
        self._encodings_cache = {}
        self._multi_samples = defaultdict(list)
    
    def _init_detector(self):
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.cascade = cv2.CascadeClassifier(cascade_path)
            else:
                import urllib.request
                url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
                os.makedirs('temp', exist_ok=True)
                urllib.request.urlretrieve(url, 'temp/haarcascade_frontalface_default.xml')
                self.cascade = cv2.CascadeClassifier('temp/haarcascade_frontalface_default.xml')
        except Exception as e:
            print(f"Could not load face detector: {e}")
            self.cascade = None
    
    def load_known_faces(self):
        encodings_file = 'face_database.pkl'
        if os.path.exists(encodings_file):
            with open(encodings_file, 'rb') as f:
                self.known_faces_data = pickle.load(f)
        else:
            self.known_faces_data = {'faces': [], 'names': []}
    
    def save_known_faces(self):
        encodings_file = 'face_database.pkl'
        with open(encodings_file, 'wb') as f:
            pickle.dump(self.known_faces_data, f)
    
    def _detect_and_crop_face(self, img):
        if not self.cascade:
            return img
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            if faces:
                x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
                return img[y:y+h, x:x+w]
        except:
            pass
        return img
    
    def add_known_face(self, name, face_image, sample_type='primary'):
        os.makedirs('faces', exist_ok=True)
        face_image = self._detect_and_crop_face(face_image)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        face_filename = f'faces/{name}_{sample_type}_{timestamp}.jpg'
        cv2.imwrite(face_filename, face_image)
        self.known_faces_data['faces'].append(face_filename)
        self.known_faces_data['names'].append(name)
        self._multi_samples[name].append(face_filename)
        self.save_known_faces()
        if name in self._encodings_cache:
            del self._encodings_cache[name]
        return face_filename
    
    def _get_face_embedding(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (128, 128))
            gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
            magnitude = np.sqrt(gx**2 + gy**2)
            angle = np.arctan2(gy, gx + 1e-8)
            bin_width = np.pi / 9
            histogram = np.zeros(18)
            for y in range(0, gray.shape[0], 8):
                for x in range(0, gray.shape[1], 8):
                    mag = magnitude[y, x]
                    ang = angle[y, x]
                    bin_idx = int((ang + np.pi) / bin_width) % 18
                    histogram[bin_idx] += mag
            if np.linalg.norm(histogram) > 0:
                histogram = histogram / np.linalg.norm(histogram)
            return histogram.astype(np.float32)
        except:
            return None
    
    def recognize_face(self, frame, return_scores=False):
        results = []
        if not self.cascade:
            return [] if return_scores else []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                face_crop = frame[y:y+h, x:x+w]
                if DEEPFACE_AVAILABLE:
                    try:
                        for i, known_path in enumerate(self.known_faces_data['faces']):
                            if not os.path.exists(known_path):
                                continue
                            known_img = cv2.imread(known_path)
                            if known_img is None:
                                continue
                            result = DeepFace.verify(face_crop, known_img,
                                model_name="VGGFace2", enforce_detection=False)
                            if result['verified']:
                                name = self.known_faces_data['names'][i]
                                if name not in [r['name'] for r in results]:
                                    results.append({'name': name, 'score': float(result.get('distance', 1.0) if isinstance(result, dict) else 1.0)})
                                break
                        continue
                    except:
                        pass
                query_embedding = self._get_face_embedding(face_crop)
                if query_embedding is None:
                    continue
                best_match = None
                best_score = 0
                name_scores = defaultdict(list)
                for i, known_path in enumerate(self.known_faces_data['faces']):
                    name = self.known_faces_data['names'][i]
                    if known_path not in self._encodings_cache:
                        known_img = cv2.imread(known_path)
                        if known_img is not None:
                            self._encodings_cache[known_path] = self._get_face_embedding(known_img)
                        else:
                            continue
                    known_embedding = self._encodings_cache.get(known_path)
                    if known_embedding is not None:
                        score = np.dot(query_embedding, known_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(known_embedding) + 1e-8)
                        name_scores[name].append(score)
                for name, scores in name_scores.items():
                    max_score = max(scores) if scores else 0
                    if max_score > 0.35 and max_score > best_score:
                        best_score = max_score
                        best_match = name
                if best_match and best_match not in [r['name'] for r in results]:
                    results.append({'name': best_match, 'score': float(best_score)})
        except Exception as e:
            print(f"Error: {e}")
        return results if return_scores else [r['name'] for r in results]
    
    def verify_student_at_interval(self, student_name, interval_minutes=10):
        now = datetime.now()
        last_verified = self.presence_log[student_name].get('last_verified')
        if last_verified is None:
            return True
        elapsed = (now - last_verified).total_seconds() / 60
        return elapsed >= interval_minutes

    def verify_student_identity(self, student_name, frame):
        now = datetime.now()
        recognition_results = self.recognize_face(frame, return_scores=True)
        detected_names = [r['name'] for r in recognition_results]
        verified = student_name in detected_names
        if verified:
            self.update_presence(student_name)
        score = next((r['score'] for r in recognition_results if r['name'] == student_name), None)
        status = 'verified' if verified else ('identity_mismatch' if detected_names else 'spoofing_attempt')
        self.verification_history[student_name].append({
            'timestamp': now.isoformat(),
            'status': status,
            'detected_names': detected_names,
            'score': score
        })
        if not verified:
            alert_type = 'identity mismatch' if detected_names else 'spoofing attempt'
            message = 'Unexpected face detected.' if detected_names else 'No recognizable face found.'
            self.add_alert(student_name, alert_type, message, detected_names)
        return verified

    def update_presence(self, student_name):
        now = datetime.now()
        if self.presence_log[student_name]['first_seen'] is None:
            self.presence_log[student_name]['first_seen'] = now
        self.presence_log[student_name]['last_seen'] = now
        self.presence_log[student_name]['count'] += 1

    def get_presence_summary(self):
        return {
            'detected': list(self.presence_log.keys()),
            'count': len(self.presence_log),
            'details': dict(self.presence_log)
        }

    def get_alert_feed(self):
        return list(self.alerts)

    def get_verification_history(self, student_name):
        return list(self.verification_history.get(student_name, []))

    def add_alert(self, student_name, alert_type, message, detected_names=None):
        now = datetime.now()
        alert = {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'student_name': student_name,
            'alert_type': alert_type,
            'message': message,
            'detected_names': detected_names or []
        }
        self.alerts.appendleft(alert)
        return alert

    def reset_session(self):
        self.reset_log()
        self.alerts.clear()
        self.verification_history.clear()
        self.verification_intervals.clear()

    def reset_log(self):
        self.presence_log = defaultdict(lambda: {'first_seen': None, 'last_seen': None, 'count': 0, 'last_verified': None})
    
    def update_verification_time(self, student_name):
        now = datetime.now()
        self.verification_intervals[student_name] = now
        self.presence_log[student_name]['last_verified'] = now

    def delete_student_data(self, student_name):
        indices_to_remove = []
        for i, name in enumerate(self.known_faces_data['names']):
            if name == student_name:
                indices_to_remove.append(i)
                if os.path.exists(self.known_faces_data['faces'][i]):
                    os.remove(self.known_faces_data['faces'][i])
        for idx in sorted(indices_to_remove, reverse=True):
            del self.known_faces_data['faces'][idx]
            del self.known_faces_data['names'][idx]
        if student_name in self._multi_samples:
            del self._multi_samples[student_name]
        keys_to_remove = [k for k in self._encodings_cache if student_name in k]
        for k in keys_to_remove:
            del self._encodings_cache[k]
        self.save_known_faces()