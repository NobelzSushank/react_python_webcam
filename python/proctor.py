# proctor.py
import cv2
import dlib
import numpy as np
from tensorflow.keras.models import load_model

class SuspiciousBehaviorAnalyzer:
    def __init__(self):
        # Face detector (dlib or OpenCV)
        self.detector = dlib.get_frontal_face_detector()
        # Head-pose landmarks predictor
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        # Emotion recognition model (e.g. FER+)
        self.emotion_model = load_model('models/model_moblenet.h5')

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray, 0)
        events = []

        if len(faces) == 0:
            events.append({'type': 'face_missing'})
        elif len(faces) > 1:
            events.append({'type': 'multiple_faces'})

        for face in faces:
            shape = self.predictor(gray, face)
            landmarks = np.array([[p.x, p.y] for p in shape.parts()])

            # Head pose (simplified)
            pitch, yaw, roll = self._estimate_head_pose(landmarks)
            if abs(yaw) > 20 or abs(pitch) > 20:
                events.append({'type': 'looking_away', 'yaw': float(yaw), 'pitch': float(pitch)})

            # Crop face and run emotion
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            face_img = cv2.resize(gray[y1:y2, x1:x2], (48, 48))
            face_img = face_img.reshape(1, 48, 48, 1) / 255.0
            emo_probs = self.emotion_model.predict(face_img)[0]
            dominant = int(np.argmax(emo_probs))
            if dominant in [3, 4]:  # e.g. “fear” or “anger”
                events.append({'type': 'suspicious_emotion', 'emotion': dominant})

        return events

    def _estimate_head_pose(self, landmarks):
        # Simplified stub: replace with solvePnP-based method
        # Returns pitch, yaw, roll in degrees
        return 0, 0, 0
