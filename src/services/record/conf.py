from pydantic import BaseModel

from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf


class RecordConf(BaseModel):
    reader: VideoReaderConf
    writer: VideoWriterConf
