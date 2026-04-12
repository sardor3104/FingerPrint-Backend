from pydantic import BaseModel, Field, field_validator

class OrganizationLocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(default=100, gt=0)

class OrganizationLocationCreate(OrganizationLocationBase):
    pass

class OrganizationLocationUpdate(OrganizationLocationBase):
    pass

class OrganizationLocationOut(OrganizationLocationBase):
    id: str

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v):
        return str(v) if v else v

    class Config:
        from_attributes = True
