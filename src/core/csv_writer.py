import csv
from .observers import Observer
from typing import List, Dict, Any

class CSVWriter(Observer):
    """Writes pose data to CSV whenever an update is received."""

    def __init__(self, filepath: str, angle_names: List[str], landmark_names: List[str]):
        self.filepath = filepath
        self._initialized = False
        self._rows = []
        self._angle_names = angle_names
        self._landmark_names = landmark_names
        self._header = self._generate_header()

    def _generate_header(self) -> List[str]:
        """Generates the CSV header based on angle and landmark names."""
        header = ["timestamp_sec"] + self._angle_names
        for lm_name in self._landmark_names:
            header += [f"{lm_name}_x", f"{lm_name}_y"]
        return header

    def update(self, timestamp: float, angles: Dict[str, float], positions: Dict[Any, tuple]):
        row = [timestamp] + [angles.get(name) for name in self._angle_names]
        for lm_name in self._landmark_names:
            # Assuming positions keys are the actual landmark objects, not their names
            # We need to find the corresponding position by iterating or by mapping landmark objects to their names
            # For now, let's assume lm_name here is the string name of the landmark
            # This part needs adjustment based on how positions are actually stored/passed
            # For now, I'll use a placeholder that assumes positions are keyed by string names
            # This will be fixed when refactoring extractor.py
            found_pos = (None, None)
            for key, value in positions.items():
                if hasattr(key, 'name') and key.name == lm_name:
                    found_pos = value
                    break
            row += [found_pos[0], found_pos[1]]
        self._rows.append(row)

    def save(self):
        """Saves the collected data to the CSV file."""
        with open(self.filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self._header)
            writer.writerows(self._rows)
            print(f"Saved csv data to: {self.filepath}")
