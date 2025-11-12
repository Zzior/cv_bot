import time
from queue import Queue
from threading import Thread, Event as TEvent
from multiprocessing import Process, Event, get_context

from .conf import InferenceConf

from ..base.abc.task import Task
from ..base.queue_utils import q_get, q_put

from services.base.detection.conf import DetectionConf
from services.base.draw_detections.conf import DrawDetectionsConf
from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf


def reader_th(out_queue: Queue, stop: TEvent, params: VideoReaderConf):
    from services.base.video_reader.node import VideoReader

    video_reader = VideoReader(params)
    try:
        for frame_element in video_reader.process():
            if stop.is_set():
                break

            if not q_put(out_queue, frame_element, stop, drop_oldest=False):
                break

    finally:
        stop.set()
        video_reader.stop()


def detect_th(in_queue: Queue, out_queue: Queue, stop: TEvent, params: DetectionConf, draw_params: DrawDetectionsConf):
    from services.base.detection.node import Detection
    from services.base.draw_detections.node import DrawDetections

    detection = Detection(params)
    draw = DrawDetections(draw_params)

    try:
        while not stop.is_set():
            frame = q_get(in_queue, stop)
            if frame is None:
                break

            detections = detection.process(frame)
            drawn_frame = draw.draw(frame, detections.xyxy, detections.confidence, detections.classes)

            if not q_put(out_queue, drawn_frame, stop):
                break
    finally:
        stop.set()

def writer_th(in_queue: Queue, stop: TEvent, params: VideoWriterConf):
    from services.base.video_writer.node import VideoWriter

    video_writer = VideoWriter(params)
    try:
        while not stop.is_set():
            frame = q_get(in_queue, stop)
            if frame is None:
                break

            video_writer.write(frame)
    finally:
        video_writer.stop()


class Inference(Task):
    def __init__(self, conf: InferenceConf):
        self.conf = conf

        self.ctx = get_context("spawn")
        self.stop_event: Event = self.ctx.Event()
        self.process: Process | None = None

    @staticmethod
    def run(conf: dict, stop: Event) -> None:
        conf_obj = InferenceConf.model_validate(conf)

        t_stop = TEvent()
        img_q = Queue(maxsize=8)
        detect_q = Queue(maxsize=8)

        threads = [
            Thread(target=reader_th, args=(img_q, t_stop, conf_obj.reader), daemon=False),
            Thread(target=detect_th, args=(img_q, detect_q, t_stop, conf_obj.detection, conf_obj.draw), daemon=False),
            Thread(target=writer_th, args=(detect_q, t_stop, conf_obj.writer), daemon=False),
        ]
        for t in threads: t.start()

        try:
            while all(t.is_alive() for t in threads) and not stop.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
        finally:
            t_stop.set()
            for t in threads: t.join(timeout=3)

    def start(self) -> None:
        self.process = self.ctx.Process(
            target=self.run,
            args=(self.conf.model_dump(), self.stop_event),
            name="inference_worker"
        )
        self.process.start()

    def stop(self) -> None:
        if not self.process:
            return

        self.stop_event.set()
        self.process.join(5)
        if self.process.is_alive():
            self.process.terminate()
