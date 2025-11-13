from typing import Generator

import cv2
import numpy as np

from .conf import VideoReaderConf


class VideoReader:
    def __init__(self, params: VideoReaderConf) -> None:
        self.params = params
        self.capture = None

        if params.roi:
            self.cut_xyxy, self.roi_mask = self.calc_roi(params.roi)
        else:
            self.cut_xyxy, self.roi_mask = None, None

    @staticmethod
    def calc_roi(roi) -> tuple[tuple[int, int, int, int], np.ndarray]:
        x = [i[0] for i in roi]
        y = [i[1] for i in roi]

        cut_xyxy = (min(x), min(y), max(x), max(y))

        out_roi = [[i[0] - cut_xyxy[0], i[1] - cut_xyxy[1]] for i in roi]
        out_roi = np.array(out_roi, dtype=np.int32)

        roi_mask = np.zeros([cut_xyxy[3] - cut_xyxy[1], cut_xyxy[2] - cut_xyxy[0]], dtype=np.uint8)
        roi_mask = cv2.fillPoly(roi_mask, [out_roi], (255, 255, 255))

        return cut_xyxy, roi_mask


    def _connect_to_stream(self) -> bool:
        if isinstance(self.capture, cv2.VideoCapture):
            self.capture.release()

        self.capture = cv2.VideoCapture(self.params.source, cv2.CAP_FFMPEG)

        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)
            return True

        return False

    def process(self) -> Generator[np.ndarray, None, None]:
        self._connect_to_stream()
        skipped_frames = 0

        try:
            while True:
                ret, frame = self.capture.read()

                if not ret:
                    self._connect_to_stream()
                    continue

                if frame is None:
                    continue

                if skipped_frames < self.params.skip_frames:
                    skipped_frames += 1
                    continue

                else:
                    skipped_frames = 0

                if self.params.roi:
                    frame = frame[
                        self.cut_xyxy[1]:self.cut_xyxy[3],
                        self.cut_xyxy[0]:self.cut_xyxy[2]
                    ]
                    frame = cv2.bitwise_and(frame, frame, mask=self.roi_mask)

                yield frame

        except KeyboardInterrupt:
            self.capture.release()

    def stop(self) -> None:
        self.capture.release()

    def __del__(self) -> None:
        self.stop()
