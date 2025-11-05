import time
import asyncio
from typing import Literal, Union
from urllib.parse import urlparse


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from numpy.typing import NDArray


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

    def picture(
            self,
            mode: Literal["numpy", "jpg"],
            draw_roi: bool = False
    ) -> tuple[Union["NDArray", bytes, None], tuple[int, int, int] | None]:
        import cv2
        import numpy as np

        capture = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not capture.isOpened():
            return None, None

        try:
            status, frame = capture.read()
            if not status:
                return None, None

            if draw_roi and self.roi:
                roi = np.array(self.roi, dtype=np.int32)
                cv2.polylines(frame, [roi], True, (0, 255, 0), 2)

            if mode == "jpg":
                status, jpeg = cv2.imencode(".jpg", frame)
                if not status:
                    return None, None
                return jpeg.tobytes(), frame.shape

            else:
                return frame, frame.shape

        finally:
            capture.release()

    def get_fps(self, calc_frames: int = 30, drop_frames: int = 15, attempts: int = 5) -> float | None:
        import cv2

        capture = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not capture.isOpened():
            return None

        dropped = 0
        frames_ts = []
        drop_attempts = 0
        calc_attempts = 0

        try:
            while dropped < drop_frames and drop_attempts < attempts:
                status = capture.grab()
                if not status:
                    drop_attempts += 1
                    continue
                dropped += 1

            while len(frames_ts) < calc_frames and calc_attempts < attempts:
                status, _ = capture.read()
                if not status:
                    calc_attempts += 1
                    continue
                frames_ts.append(time.perf_counter())

            if len(frames_ts) > 1:
                return (len(frames_ts) - 1) / (frames_ts[-1] - frames_ts[0])
            else:
                return None
        finally:
            capture.release()
