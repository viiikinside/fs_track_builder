from abc import ABC, abstractmethod
import pygame
from typing import Tuple, Dict, Any

class TrackElement(ABC):
    def __init__(self, element_type: str, start_pos: Tuple[float, float], **kwargs: Any) -> None:
        self.type = element_type
        self.start_pos = start_pos
        self.properties = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'start': self.start_pos,
            **self.properties
        }

    @abstractmethod
    def draw(self, screen):
        pass

class StraightElement(TrackElement):
    def __init__(self, start_pos, length, angle=0):
        super().__init__('straight', start_pos, length=length, angle=angle)
        self.angle = angle

    def draw(self, screen):
        # Implementation for drawing straight track segment
        pass

class CurveElement(TrackElement):
    def __init__(self, start_pos, radius, angle):
        super().__init__('curve', start_pos, radius=radius, angle=angle)
        self.radius = radius
        self.angle = angle

    def draw(self, screen):
        # Implementation for drawing curved track segment
        pass
