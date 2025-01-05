from typing import Optional
import requests
import logging

from xtts_rvc_client.types import (
    GenerateAudioRequest,
    HealthCheckResponse,
)

_LOGGER = logging.getLogger(__name__)


class XTTSRVCClient:

    def __init__(self, host: str, port: str) -> None:
        self.host = host
        self.port = port

    def health_check(self) -> bool:
        try:
            res = requests.get(f"http://{self.host}:{self.port}/health")
            res_json = HealthCheckResponse(**res.json())
            if res_json.status != "ready":
                return False
            return True
        except Exception as e:
            _LOGGER.error(e)
            return False

    def generate_audio(self, request_data: GenerateAudioRequest) -> Optional[bytes]:
        """
        Sends a text message to the server to generate audio and returns the audio bytes.

        Args:
            request_data (GenerateAudioRequest): The request data containing the message to generate audio for.

        Returns:
            Optional[bytes]: The audio bytes if the request is successful, None otherwise.
        """
        try:
            url = f"http://{self.host}:{self.port}/generate"
            payload = request_data.model_dump()
            headers = {"Content-Type": "application/json"}

            res = requests.post(url, json=payload, headers=headers)

            if res.status_code == 200:
                return res.content
            else:
                _LOGGER.error(
                    f"Audio generation failed: {res.status_code} - {res.text}"
                )
                return None
        except Exception as e:
            _LOGGER.error(f"Error during audio generation: {e}")
            return None
