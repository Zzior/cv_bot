from typing import Generator

import cv2

from .conf import VideoReaderConf

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np


class VideoReader:
    def __init__(self, params: VideoReaderConf) -> None:
        self.params = params
        self.capture = None

    def _connect_to_stream(self) -> bool:
        if isinstance(self.capture, cv2.VideoCapture):
            self.capture.release()

        self.capture = cv2.VideoCapture(self.params.source, cv2.CAP_FFMPEG)

        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)
            return True

        return False

    def process(self) -> Generator["np.ndarray", None, None]:
        self._connect_to_stream()

        try:
            while True:
                ret, frame = self.capture.read()

                if not ret:
                    self._connect_to_stream()
                    continue

                if frame is None:
                    continue

                yield frame

        except KeyboardInterrupt:
            self.capture.release()

    def stop(self) -> None:
        self.capture.release()

    def __del__(self) -> None:
        self.stop()
