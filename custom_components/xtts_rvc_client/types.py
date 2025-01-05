from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str


class GenerateAudioRequest(BaseModel):
    message: str
