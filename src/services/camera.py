import asyncio
from urllib.parse import urlparse


class Camera:
    def __init__(self, source: str, roi: list[list[int]] | None = None, timeout_s: float = 5.0):
        self.source = source
        self.roi = roi
        self.timeout_s = timeout_s

    async def ping(self) -> bool:
        parsed = urlparse(self.source)
        if not parsed.hostname:
            return False

        try:
            _ = parsed.port
        except ValueError:
            return False

        if not parsed.port:
            if parsed.scheme in ("rtsp", "rtsps"):
                port = 554
            elif parsed.scheme == "http":
                port = 80
            elif parsed.scheme == "https":
                port = 443
            else:
                return False
        else:
            port = parsed.port

        try:
            await asyncio.wait_for(
                asyncio.open_connection(parsed.hostname, port),
                self.timeout_s
            )
            return True

        except Exception as e:
            _ = e
            return False
