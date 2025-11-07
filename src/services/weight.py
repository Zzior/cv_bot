from pathlib import Path

import cv2
import torch
import numpy as np
from ultralytics import YOLO

from services.base.draw_detections.node import DrawDetections
from services.base.draw_detections.conf import DrawDetectionsConf


class Weight:
    def __init__(
            self, path: str | Path,
            iou: float = 0.7,
            confidence: float = 0.25,
            device: str | None = None,
    ) -> None:
        self.path = path
        self.model = YOLO(self.path)
        self.draw = DrawDetections(DrawDetectionsConf(classes_names=self.get_classes()))

        self.iou = iou
        self.confidence = confidence

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

    def get_classes(self) -> dict[int, str]:
        return self.model.names

    @staticmethod
    def to_numpy(image: bytes) -> np.ndarray:
        image_array = np.frombuffer(image, np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    @staticmethod
    def from_numpy(image: np.ndarray, ext: str = ".jpg") -> bytes | None:
        status, jpeg = cv2.imencode(ext, image)
        if status:
            return jpeg.tobytes()
        else:
            return None

    def detect(self, image: np.ndarray) -> np.ndarray:
        outputs = self.model.predict(image, verbose=False, iou=self.iou, conf=self.confidence)

        detect_xyxy = outputs[0].boxes.xyxy.cpu().int().tolist()
        detect_conf = outputs[0].boxes.conf.cpu().tolist()
        detect_cls = outputs[0].boxes.cls.cpu().int().tolist()

        drawn_image = self.draw.draw(image, detect_xyxy, detect_conf, detect_cls)
        return drawn_image
