from pydantic import BaseModel


class GetAllUploadsResponse(BaseModel):
    uploads: list[str]
