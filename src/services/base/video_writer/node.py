from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import av
import numpy as np

from .conf import VideoWriterConf


class VideoWriter:
    def __init__(self, params: VideoWriterConf):
        self.params = params

        self.save_dir = Path(params.save_dir)
        self.timezone = ZoneInfo(self.params.timezone)
        self.segment_frames = int(self.params.fps * self.params.segment_size)

        Path.mkdir(self.save_dir, parents=True, exist_ok=True)

        self.frames_in_segment = 0
        self.container = None
        self.stream = None

    def _create_new_writer(self, shape):
        timestamp = datetime.now(self.timezone).strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"{timestamp}.mkv"

        self.container = av.open(str(filename), mode="w")
        self.stream = self.container.add_stream(self.params.codec, rate=self.params.fps)
        self.stream.width = shape[1]
        self.stream.height = shape[0]
        self.stream.pix_fmt = self.params.pix_fmt
        self.stream.bit_rate = self.params.bitrate

    def write(self, frame: np.ndarray) -> None:
        if self.container is None:
            self._create_new_writer(frame.shape)

        write_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")

        for packet in self.stream.encode(write_frame):
            self.container.mux(packet)

        self.frames_in_segment += 1

        if self.frames_in_segment >= self.segment_frames:
            self._close_current_writer()
            self.frames_in_segment = 0
            self._create_new_writer(frame.shape)

    def _close_current_writer(self):
        if self.container:
            for packet in self.stream.encode():
                self.container.mux(packet)
            self.container.close()
            self.container = None
            self.stream = None

    def stop(self):
        self._close_current_writer()

    def __del__(self):
        self._close_current_writer()
