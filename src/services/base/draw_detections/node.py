import time

import cv2
import numpy as np

from .conf import DrawDetectionsConf

class FPSCounter:
    def __init__(self, buffer_size: int = 60):
        self.time_buffer = []
        self.buffer_size = buffer_size

    def get_fps(self) -> float:
        self.time_buffer.append(time.time())

        if len(self.time_buffer) < self.buffer_size:
            return 0.0

        return (self.buffer_size - 1) / (self.time_buffer[-1] - self.time_buffer.pop(0))


class DrawDetections:
    def __init__(self, params: DrawDetectionsConf):
        self.params = params
        self.fps = FPSCounter()

    def draw(
            self,
            frame: np.ndarray,
            xyxy: list[list[int]],
            confidence: list[float],
            classes: list[int],
    ) -> np.ndarray:
        out_frame = frame.copy()

        self.draw_boxes(out_frame, xyxy, confidence, classes)

        if self.params.show_fps:
            self.draw_fps(out_frame)

        return out_frame


    def draw_boxes(self, frame: np.ndarray, xyxy, confidence, classes) -> np.ndarray:
        for xyxy, confidence, classes in zip(xyxy, confidence, classes):
            color = self.get_color(classes)

            cv2.rectangle(
                frame,
                (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]),
                color,
                self.params.thickness
            )

            label = (
                f"{self.params.classes_names.get(classes, classes)} "
                f"{round(confidence, 2) if self.params.show_confidence else ''}"
            )
            cv2.putText(
                frame,
                label,
                (xyxy[0] + 5, xyxy[1] + 30),
                self.params.font,
                self.params.font_scale,
                color,
                self.params.thickness,
            )

        return frame

    def draw_fps(self, frame: np.ndarray) -> np.ndarray:
        fps = self.fps.get_fps()
        cv2.putText(
            frame,
            f"FPS: {round(fps, 2)}",
            (10, 30),
            self.params.font,
            self.params.font_scale,
            (0, 255, 0),
            self.params.thickness,
        )
        return frame

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