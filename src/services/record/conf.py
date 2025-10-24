from typing import Literal
from pydantic import BaseModel, ConfigDict

from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf


class RecordConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    kind: Literal["record"] = "record"

    reader: VideoReaderConf
    writer: VideoWriterConf
