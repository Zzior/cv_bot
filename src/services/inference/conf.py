from typing import Literal
from pydantic import BaseModel, ConfigDict

from services.base.detection.conf import DetectionConf
from services.base.draw_detections.conf import DrawDetectionsConf
from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf


class InferenceConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["inference"] = "inference"

    reader: VideoReaderConf
    detection: DetectionConf
    draw: DrawDetectionsConf
    writer: VideoWriterConf
