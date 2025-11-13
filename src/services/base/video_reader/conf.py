from pydantic import BaseModel, ConfigDict, Field


class VideoReaderConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str
    skip_frames: int = 0
    roi: list[list[int]] = Field(default_factory=list)