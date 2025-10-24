from pydantic import BaseModel, ConfigDict


class VideoReaderConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
