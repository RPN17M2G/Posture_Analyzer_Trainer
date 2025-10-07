import cv2
import numpy as np
import csv
from typing import List, Dict, Any, Tuple, Callable

from core.visualizer import PoseVisualizer
from core.angle_definitions import angle_definitions
from core.angle_utils import extract_angles_from_landmarks
import mediapipe as mp
from config import Config


class PostureTrainer:
    """Handles live camera feed comparison against reference CSV."""

    class DisplayMode:
        USER_FEEDBACK = 0
        REFERENCE_ONLY = 1
        Count = 2

    def __init__(self, config: Config):
        self.config = config
        self.pose_detector = mp.solutions.pose.Pose(
            min_detection_confidence=self.config.MIN_DETECTION_CONFIDENCE
        )

        self.DISPLAY_MODE_NAMES = {
            self.DisplayMode.USER_FEEDBACK: "User Feedback",
            self.DisplayMode.REFERENCE_ONLY: "Reference Only",
        }

        self.ref_angles_list: List[Dict[str, float]] = []
        self.ref_positions_list: List[Dict[mp.solutions.pose.PoseLandmark, Tuple[float, float]]] = []
        self.load_reference_data()

        # Map display modes to processing lambdas
        self._display_actions: Dict[int, Callable[[Any, int, Dict, Dict], Any]] = {
            self.DisplayMode.USER_FEEDBACK: self._draw_user_feedback,
            self.DisplayMode.REFERENCE_ONLY: self._draw_reference_only
        }

    def load_reference_data(self):
        """Loads reference angles and positions from the CSV file."""
        with open(self.config.REF_CSV_PATH, newline="") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            angles = {
                k: float(v) if v else None
                for k, v in row.items()
                if k in angle_definitions
            }

            positions = {
                lm_name: (
                    float(row.get(f"{lm_name.name}_x", None)),
                    float(row.get(f"{lm_name.name}_y", None))
                ) if row.get(f"{lm_name.name}_x") and row.get(f"{lm_name.name}_y") else (None, None)
                for lm_name in mp.solutions.pose.PoseLandmark
            }

            self.ref_angles_list.append(angles)
            self.ref_positions_list.append(positions)

    def _process_camera_frame(self, frame: Any) -> Tuple[Dict[mp.solutions.pose.PoseLandmark, Tuple[float, float]], Dict[str, float], Any]:
        """Processes a single camera frame to extract pose data."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(rgb_frame)

        landmarks = results.pose_landmarks.landmark if results.pose_landmarks else []
        current_positions = {
            lm_name: (landmarks[lm_name.value].x, landmarks[lm_name.value].y)
            for lm_name in mp.solutions.pose.PoseLandmark
            if lm_name.value < len(landmarks)
        }
        current_angles = extract_angles_from_landmarks(landmarks, angle_definitions) if landmarks else {}

        return current_positions, current_angles, frame

    @staticmethod
    def _resize_frames(ref_frame: Any, cam_frame: Any) -> Tuple[Any, Any]:
        """Resizes reference and camera frames for consistent display."""
        h_cam, w_cam = cam_frame.shape[:2]
        h_ref, w_ref = ref_frame.shape[:2]

        ref_frame_resized = cv2.resize(ref_frame, (int(w_ref * h_cam / h_ref), h_cam))
        cam_frame_resized = cv2.resize(cam_frame, (w_cam, h_cam))

        return ref_frame_resized, cam_frame_resized

    def _draw_user_feedback(self, frame: Any, idx: int, positions: Dict, angles: Dict) -> Any:
        return PoseVisualizer.draw_skeleton(
            frame,
            positions,
            angle_definitions,
            angles=angles,
            ref_angles=self.ref_angles_list[idx],
            threshold=self.config.TRAINER_THRESHOLD,
            show_user=True
        )

    def _draw_reference_only(self, frame: Any, idx: int, positions: Dict, angles: Dict) -> Any:
        return PoseVisualizer.draw_skeleton(
            frame,
            self.ref_positions_list[idx],
            angle_definitions,
            show_user=False
        )

    def start(self):
        """Starts the live posture training session."""
        ref_cap = cv2.VideoCapture(self.config.REF_VIDEO_PATH)
        cam_cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        frame_index = 0
        display_mode = self.DisplayMode.USER_FEEDBACK

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

            if frame_index < len(self.ref_angles_list):
                cam_frame_resized = self._display_actions[display_mode](
                    cam_frame_resized, frame_index, current_positions, current_angles
                )

            combined_frame = np.hstack((ref_frame_resized, cam_frame_resized))
            combined_frame = PoseVisualizer.display_mode(combined_frame, self.DISPLAY_MODE_NAMES[display_mode])
            cv2.imshow(self.config.WINDOW_NAME, combined_frame)

            key = cv2.waitKey(self.config.WAIT_KEY_DELAY) & 0xFF
            if key == ord(self.config.EXIT_KEY):
                break
            if key == ord(self.config.TOGGLE_MODE_KEY):
                display_mode = ((display_mode + 1) % self.DisplayMode.Count)  # cycles forward
           
            frame_index += 1

        ref_cap.release()
        cam_cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.close()
