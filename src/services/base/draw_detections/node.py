import cv2
import numpy as np

from .conf import DrawDetectionConf


class DrawDetections:
    def __init__(self, params: DrawDetectionConf):
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
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Purple
            (0, 255, 255),  # Blue
            (255, 20, 147),  # Deep Pink
            (255, 165, 0),  # Orange
            (32, 178, 170),  # Light Sea
            (148, 0, 211)  # Dark Violet
        ]

        return colors[id_ % 10]