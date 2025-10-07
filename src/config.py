import os

class Config:
    """Manages configuration settings for the application."""

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.REF_CSV_PATH = "Fill your desired CSV path to store analyzed reference data here"
        self.REF_VIDEO_PATH = "Fill your reference video path here"
        self.MIN_DETECTION_CONFIDENCE = 0.5
        self.TRAINER_THRESHOLD = 10
        self.CAMERA_INDEX: int = 0  
        self.WINDOW_NAME: str = "Posture Trainer"
        self.EXIT_KEY: str = "q"
        self.TOGGLE_MODE_KEY: str = "m"
        self.WAIT_KEY_DELAY: int = 10
