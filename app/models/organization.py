from beanie import Document
from pydantic import Field

class OrganizationLocation(Document):
    """
    Stores the organization's central location and acceptable attendance radius.
    Only one instance of this should exist ideally for a single-site organization.
    """
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(default=100, gt=0)

    class Settings:
        name = "organization_location"
