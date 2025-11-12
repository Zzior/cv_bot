from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict


class DetectionConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    weights_path: str
    device: str | None = None

    classes: list[int] | None = None
    confidence: float = 0.25
    iou: float = 0.7


@dataclass
class DetectionOutputs:
    xyxy: list[list[int]]
    confidence: list[float]
    classes: list[int]