import math

from .angle_definitions import angle_definitions

def get_landmark_coordinates(landmarks, landmark_id):
    """Extracts (x, y) coordinates for a given landmark ID."""
    return (landmarks[landmark_id.value].x, landmarks[landmark_id.value].y)

def calculate_angle(point_a, point_b, point_c):
    """Calculates the angle between three points."""
    vector_ab = (point_a[0] - point_b[0], point_a[1] - point_b[1])
    vector_cb = (point_c[0] - point_b[0], point_c[1] - point_b[1])

    dot_product = vector_ab[0] * vector_cb[0] + vector_ab[1] * vector_cb[1]
    magnitude_ab = math.sqrt(vector_ab[0]**2 + vector_ab[1]**2)
    magnitude_cb = math.sqrt(vector_cb[0]**2 + vector_cb[1]**2)

    if magnitude_ab == 0 or magnitude_cb == 0:
        return None

    cosine_angle = max(-1, min(1, dot_product / (magnitude_ab * magnitude_cb)))
    return math.degrees(math.acos(cosine_angle))

def extract_angles_from_landmarks(landmarks, angle_defs_map):
    """Extracts angles from MediaPipe landmarks based on angle definitions."""
    angles = {}
    for name, (landmark_a, landmark_b, landmark_c) in angle_defs_map.items():
        try:
            point_a = get_landmark_coordinates(landmarks, landmark_a)
            point_b = get_landmark_coordinates(landmarks, landmark_b)
            point_c = get_landmark_coordinates(landmarks, landmark_c)
            angles[name] = calculate_angle(point_a, point_b, point_c)
        except IndexError: # Handle cases where a landmark might be missing
            angles[name] = None
        except Exception as e: # Catch other potential errors
            print(f"Error calculating angle for {name}: {e}")
            angles[name] = None
    return angles
