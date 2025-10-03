import os

class Config:
    """Manages configuration settings for the application."""

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.REF_CSV_PATH = os.path.join(self.BASE_DIR, "..", "ref.csv")
        self.REF_VIDEO_PATH = os.path.join(self.BASE_DIR, "..", "WIN_20251003_22_40_41_Pro.mp4")
        self.MIN_DETECTION_CONFIDENCE = 0.5
        self.TRAINER_THRESHOLD = 10