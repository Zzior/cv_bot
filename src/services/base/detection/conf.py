from pydantic import BaseModel, ConfigDict


class DetectionConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    weights_path: str
    device: str | None = None

    classes: list[int] | None = None
    confidence: float = 0.25
    iou: float = 0.7