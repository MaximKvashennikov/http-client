from pydantic import BaseModel, ConfigDict, Field


class Category(BaseModel):
    id: int | None = None
    name: str | None = None


class Tag(BaseModel):
    id: int | None = None
    name: str | None = None


class Pet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str
    category: Category | None = None
    photo_urls: list[str] = Field(
        default_factory=list,
        alias="photoUrls",
        serialization_alias="photoUrls",
    )
    tags: list[Tag] | None = None
    status: str | None = None
