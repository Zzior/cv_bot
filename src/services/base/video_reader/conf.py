from pydantic import BaseModel


class VideoReaderConf(BaseModel):
    source: str
