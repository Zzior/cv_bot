from pydantic import BaseModel, ConfigDict, Field


class DrawDetectionsConf(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classes_names: dict[int, str] = Field(default_factory=dict)
    show_confidence: bool = True

    thickness: int = 2

    font: int = 1
    font_scale: float = 1.5
