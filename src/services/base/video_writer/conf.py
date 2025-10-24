from pydantic import BaseModel, ConfigDict


class VideoWriterConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    fps: int
    save_dir: str

    timezone: str = "UTC"

    segment_size: int = 3600
    codec: str = "h264"
    pix_fmt: str = "yuv420p"
    bitrate: int = 10_000_000
