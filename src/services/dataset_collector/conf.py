from typing import Literal
from pydantic import BaseModel, ConfigDict

from services.base.detection.conf import DetectionConf
from services.base.video_reader.conf import VideoReaderConf


class DatasetCollectorConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["dataset_collector"] = "dataset_collector"

    save_dir: str

    reader: VideoReaderConf
    detection: DetectionConf | None = None

    classes_conf: dict[int, tuple[float, float]]
    ignore_zone_ratio: int = 10