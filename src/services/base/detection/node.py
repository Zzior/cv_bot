import torch
import numpy as np
from ultralytics import YOLO

from .conf import DetectionConf, DetectionOutputs


class Detection:
    def __init__(self, params: DetectionConf) -> None:
        self.params = params
        self.model = YOLO(params.weights_path)
        self.names = self.model.names

        if self.params.device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.params.device)

    def process(self, frame: np.ndarray) -> DetectionOutputs:
        outputs = self.model.predict(
            frame,
            verbose=False,
            classes=self.params.classes,
            conf=self.params.confidence,
            iou=self.params.iou,
        )

        return DetectionOutputs(
            xyxy=outputs[0].boxes.xyxy.cpu().int().tolist(),
            confidence=outputs[0].boxes.conf.cpu().tolist(),
            classes=outputs[0].boxes.cls.cpu().int().tolist()
        )
