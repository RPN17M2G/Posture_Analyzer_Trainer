import cv2
import numpy as np
import csv
from typing import List, Dict, Any, Tuple

from core.visualizer import PoseVisualizer
from core.angle_defs import angle_definitions
from core.angle_utils import extract_angles_from_landmarks
import mediapipe as mp
from config import Config

class PostureTrainer:
    """Handles live camera feed comparison against reference CSV."""

    def __init__(self, config: Config):
        self.config = config
        self.pose_detector = mp.solutions.pose.Pose(min_detection_confidence=self.config.MIN_DETECTION_CONFIDENCE)
        self.ref_angles_list: List[Dict[str, float]] = []
        self.ref_positions_list: List[Dict[mp.solutions.pose.PoseLandmark, Tuple[float, float]]] = []
        self.load_reference_data()

    def load_reference_data(self):
        """Loads reference angles and positions from the CSV file."""
        with open(self.config.REF_CSV_PATH, newline="") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            angles = {k: float(v) if v else None for k, v in row.items() if k in angle_definitions}
            positions = {}
            for lm_name in mp.solutions.pose.PoseLandmark:
                x_key = f"{lm_name.name}_x"
                y_key = f"{lm_name.name}_y"
                if x_key in row and y_key in row and row[x_key] and row[y_key]:
                    positions[lm_name] = (float(row[x_key]), float(row[y_key]))
                else:
                    positions[lm_name] = (None, None) # Or handle as appropriate for missing data
            self.ref_angles_list.append(angles)
            self.ref_positions_list.append(positions)

    def _process_camera_frame(self, frame: Any) -> Tuple[Dict[mp.solutions.pose.PoseLandmark, Tuple[float, float]], Dict[str, float], Any]:
        """Processes a single camera frame to extract pose data."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(rgb_frame)

        current_positions = {}
        current_angles = {}

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            current_positions = {lm_name: (landmarks[lm_name.value].x, landmarks[lm_name.value].y)
                                 for lm_name in mp.solutions.pose.PoseLandmark if lm_name.value < len(landmarks)}
            current_angles = extract_angles_from_landmarks(landmarks, angle_definitions)
        return current_positions, current_angles, frame

    def _resize_frames(self, ref_frame: Any, cam_frame: Any) -> Tuple[Any, Any]:
        """Resizes reference and camera frames for consistent display."""
        h_cam, w_cam = cam_frame.shape[:2]
        h_ref, w_ref = ref_frame.shape[:2]
        ref_frame_resized = cv2.resize(ref_frame, (int(w_ref * h_cam / h_ref), h_cam))
        cam_frame_resized = cv2.resize(cam_frame, (w_cam, h_cam))
        return ref_frame_resized, cam_frame_resized

    def start(self):
        """Starts the live posture training session."""
        ref_cap = cv2.VideoCapture(self.config.REF_VIDEO_PATH)
        cam_cap = cv2.VideoCapture(0)  # 0 for default camera
        frame_idx = 0
        display_mode = 1  # 1: user feedback, 2: reference only

        while True:
            success_ref, ref_frame = ref_cap.read()
            success_cam, cam_frame = cam_cap.read()

            if not success_cam:
                print("Failed to grab camera frame.")
                break
            if not success_ref:
                break  # End of reference video

            current_positions, current_angles, cam_frame_processed = self._process_camera_frame(cam_frame)
            ref_frame_resized, cam_frame_resized = self._resize_frames(ref_frame, cam_frame_processed)

            if frame_idx < len(self.ref_angles_list):
                if display_mode == 1:
                    cam_frame_resized = PoseVisualizer.draw_skeleton(
                        cam_frame_resized, current_positions, angle_definitions,
                        angles=current_angles,
                        ref_angles=self.ref_angles_list[frame_idx],
                        threshold=self.config.TRAINER_THRESHOLD,
                        show_user=True
                    )
                else: # display_mode == 2
                    cam_frame_resized = PoseVisualizer.draw_skeleton(
                        cam_frame_resized, self.ref_positions_list[frame_idx], angle_definitions,
                        show_user=False
                    )

            combined_frame = np.hstack((ref_frame_resized, cam_frame_resized))
            combined_frame = PoseVisualizer.display_mode(combined_frame, display_mode)
            cv2.imshow("Posture Trainer", combined_frame)

            key = cv2.waitKey(10) & 0xFF
            if key == ord("q"):
                break
            if key == ord("m"):
                display_mode = 2 if display_mode == 1 else 1
            frame_idx += 1

        ref_cap.release()
        cam_cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.close()
