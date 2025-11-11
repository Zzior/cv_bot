import cv2
import numpy as np

from .conf import DrawDetectionsConf


class DrawDetections:
    def __init__(self, params: DrawDetectionsConf):
        self.params = params

    def draw(
            self,
            frame: np.ndarray,
            xyxy: list[list[int]],
            confidence: list[float],
            classes: list[int],
    ) -> np.ndarray:
        out_frame = frame.copy()

        for xyxy, confidence, classes in zip(xyxy, confidence, classes):
            color = self.get_color(classes)

            cv2.rectangle(
                out_frame,
                (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]),
                color,
                self.params.thickness
            )

            label = (
                f"{self.params.classes_names.get(classes, classes)} "
                f"{round(confidence, 2) if self.params.show_confidence else ''}"
            )
            cv2.putText(
                out_frame,
                label,
                (xyxy[0] + 5, xyxy[1] + 30),
                self.params.font,
                self.params.font_scale,
                color,
                self.params.thickness,
            )

        return out_frame

    @staticmethod
    def get_color(id_: int) -> tuple[int, int, int]:
        colors = [
            (0, 255, 255),   # Yellow
            (255, 255, 0),   # Blue
            (0, 255, 0),     # Green
            (0, 165, 255),   # Orange
            (170, 178, 32),  # Light Sea
            (147, 20, 255),  # Deep Pink
            (255, 0, 255),   # Purple
            (0, 0, 255),     # Red
            (211, 0, 148),   # Dark Violet
            (255, 0, 0)      # Blue
        ]

        return colors[id_ % 10]