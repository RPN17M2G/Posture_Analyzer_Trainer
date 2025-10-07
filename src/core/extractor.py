import cv2
import mediapipe as mp
from .angle_utils import extract_angles_from_landmarks
from .angle_definitions import angle_definitions

class PoseExtractor:
    """Extracts pose data from video and notifies observers."""

    def __init__(self, static_mode: bool = False, confidence: float = 0.5):
        self.pose_detector = mp.solutions.pose.Pose(static_image_mode=static_mode,
                                          min_detection_confidence=confidence)
        self.observers = []
        self.angle_definitions = angle_definitions

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, timestamp: float, angles: dict[str, float], positions: dict[mp.solutions.pose.PoseLandmark, tuple]):
        """Notifies all attached observers with the extracted pose data."""
        for obs in self.observers:
            obs.update(timestamp, angles, positions)

    def _extract_landmark_positions(self, landmarks) -> dict[mp.solutions.pose.PoseLandmark, tuple]:
        """Extracts (x, y) positions for all MediaPipe pose landmarks."""
        positions = {}
        for lm_name in mp.solutions.pose.PoseLandmark:
            idx = lm_name.value
            if idx < len(landmarks):
                positions[lm_name] = (landmarks[idx].x, landmarks[idx].y)
        return positions

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_idx = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_idx += 1
            timestamp = frame_idx / fps
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(rgb_frame)

            angles = {}
            positions = {}
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                angles = extract_angles_from_landmarks(landmarks, self.angle_definitions)
                positions = self._extract_landmark_positions(landmarks)

            self.notify(timestamp, angles, positions)

        cap.release()
        self.pose_detector.close()
