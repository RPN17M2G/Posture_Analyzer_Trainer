from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, timestamp, angles, positions):
        """Called by PoseExtractor whenever new frame data is available."""
        pass
