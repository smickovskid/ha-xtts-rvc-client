import httpx
import logging
from typing import Optional

from .types import HealthCheckResponse, GenerateAudioRequest

_LOGGER = logging.getLogger(__name__)


class XTTSRVCClient:

    def __init__(self, host: str, port: str) -> None:
        self.host = host
        self.port = port

    async def health_check(self) -> bool:
        """
        Asynchronously checks the health status of the server.

        Returns:
            bool: True if the server is ready, False otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"http://{self.host}:{self.port}/health")
                res_json = HealthCheckResponse(**res.json())
                return res_json.status == "ready"
        except Exception as e:
            _LOGGER.error(f"Health check failed: {e}")
            return False

    async def generate_audio(self, request_data: GenerateAudioRequest) -> Optional[bytes]:
        """
        Sends a text message to the server to generate audio asynchronously and returns the audio bytes.

        Args:
            request_data (GenerateAudioRequest): The request data containing the message to generate audio for.

        Returns:
            Optional[bytes]: The audio bytes if the request is successful, None otherwise.
        """
        try:
            url = f"http://{self.host}:{self.port}/generate"
            payload = request_data.dict()  # Replace with .dict() if using Pydantic v1.x
            headers = {"Content-Type": "application/json"}

            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=59)

                if res.status_code == 200:
                    _LOGGER.info("Audio generation successful.")
                    return res.content  # Return the audio bytes
                else:
                    _LOGGER.error(f"Audio generation failed: {res.status_code} - {res.text}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Error during audio generation: {e}")
            return None
