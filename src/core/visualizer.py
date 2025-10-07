import cv2
from typing import Dict, Tuple, Any
import mediapipe as mp

class PoseVisualizer:
    """Draws skeleton and feedback on frames."""

    @staticmethod
    def draw_skeleton(frame: Any, positions: Dict[mp.solutions.pose.PoseLandmark, Tuple[float, float]],
                      angle_definitions: Dict[str, Tuple[mp.solutions.pose.PoseLandmark, mp.solutions.pose.PoseLandmark, mp.solutions.pose.PoseLandmark]],
                      angles: Dict[str, float] = None, ref_angles: Dict[str, float] = None,
                      threshold: int = 10, show_user: bool = True) -> Any:
        """Draws the skeleton and provides feedback on the frame."""
        h, w, _ = frame.shape
        for joint_name, (landmark_a, landmark_b, landmark_c) in angle_definitions.items():
            try:
                point_a = positions.get(landmark_a)
                point_b = positions.get(landmark_b)
                point_c = positions.get(landmark_c)

                if point_a and point_b and point_c:
                    color = (0, 255, 0)  # Green for correct posture
                    if show_user and angles and ref_angles:
                        current_angle = angles.get(joint_name)
                        reference_angle = ref_angles.get(joint_name)
                        if current_angle is not None and reference_angle is not None:
                            if abs(current_angle - reference_angle) > threshold:
                                color = (0, 0, 255)  # Red for incorrect posture

                    # Convert normalized coordinates to pixel coordinates
                    p1 = (int(point_a[0] * w), int(point_a[1] * h))
                    p2 = (int(point_b[0] * w), int(point_b[1] * h))
                    p3 = (int(point_c[0] * w), int(point_c[1] * h))

                    # Draw lines for bones
                    cv2.line(frame, p1, p2, color, 3)
                    cv2.line(frame, p2, p3, color, 3)

                    # Draw circles for joints
                    cv2.circle(frame, p1, 5, color, -1)
                    cv2.circle(frame, p2, 5, color, -1)
                    cv2.circle(frame, p3, 5, color, -1)
            except Exception as e:
                print(f"Error drawing joint {joint_name}: {e}")
                continue
        return frame

    @staticmethod
    def display_mode(frame: Any, mode: int) -> Any:
        """Displays the current mode on the frame."""
        cv2.putText(frame, f"Mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        return frame
