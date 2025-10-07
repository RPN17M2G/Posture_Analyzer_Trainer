from config import Config
from core.extractor import PoseExtractor
from core.pose_data_csv_writer import PoseDataCSVWriter
from trainer.posture_trainer import PostureTrainer
from core.angle_definitions import angle_definitions
import mediapipe as mp

def main():
    config = Config()

    # Extract reference data
    extractor = PoseExtractor(confidence=config.MIN_DETECTION_CONFIDENCE)
    writer = PoseDataCSVWriter(config.REF_CSV_PATH, list(angle_definitions.keys()), [lm.name for lm in mp.solutions.pose.PoseLandmark])
    extractor.attach(writer)
    extractor.process_video(config.REF_VIDEO_PATH)
    writer.save()

    # Start live posture trainer
    trainer = PostureTrainer(config)
    trainer.start()

if __name__ == "__main__":
    main()
