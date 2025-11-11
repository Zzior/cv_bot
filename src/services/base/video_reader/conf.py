from pydantic import BaseModel, ConfigDict, Field


class VideoReaderConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: str

    roi: list[list[int]] = Field(default_factory=list)