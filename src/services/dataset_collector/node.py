import time
from queue import Queue
from pathlib import Path
from datetime import datetime
from threading import Thread, Event as TEvent
from multiprocessing import Process, Event, get_context

from .conf import DatasetCollectorConf
from .tools import get_roi, get_yolo_label, calc_c_point

from ..base.abc.task import Task
from ..base.queue_utils import q_get, q_put

from services.base.video_reader.conf import VideoReaderConf
from services.base.detection.conf import DetectionConf, DetectionOutputs



def get_label(detections: DetectionOutputs, params: DatasetCollectorConf, shape: tuple[int, int]) -> str:
    import numpy as np
    import cv2

    yolo_label = ""
    save = False
    roi = np.array(get_roi(shape, params.ignore_zone_ratio), dtype=np.int32)


    for xyxy, conf, cls in zip(detections.xyxy, detections.confidence, detections.classes):
        if cls not in params.classes_conf:
            continue

        if (
                (params.classes_conf[cls][0] < conf < params.classes_conf[cls][1])
                and (cv2.pointPolygonTest(roi, calc_c_point(xyxy), False) >= 0)
        ):
            save = True

        yolo_label += get_yolo_label(cls, xyxy, shape)

    if save:
        return yolo_label
    else:
        return ""


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


def detect_th(in_queue: Queue, out_queue: Queue, stop: TEvent, params: DetectionConf):
    from services.base.detection.node import Detection

    detection = Detection(params)
    try:
        while not stop.is_set():
            frame = q_get(in_queue, stop)
            if frame is None:
                break

            detections = detection.process(frame)

            if not q_put(out_queue, [frame, detections], stop):
                break
    finally:
        stop.set()


def writer_th(in_queue: Queue, stop: TEvent, params: DatasetCollectorConf):
    import cv2

    try:
        save_dir = Path(params.save_dir)
        images_dir = save_dir / "images/Train"
        labels_dir = save_dir / "labels/Train"
        for path in (images_dir, labels_dir, save_dir / "images/Validation", save_dir / "labels/Validation"):
            path.mkdir(parents=True, exist_ok=True)

        while not stop.is_set():
            item = q_get(in_queue, stop)
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            if item is None:
                break

            elif isinstance(item, list):
                frame = item[0]
                detections = item[1]
                label = get_label(detections, params, (frame.shape[1], frame.shape[0]))
                if label:
                    cv2.imwrite(f"{images_dir.resolve().__str__()}/{now_str}.png", frame)
                    with open(f"{labels_dir.resolve().__str__()}/{now_str}.txt", "w") as f:
                        f.write(label)

            else:
                cv2.imwrite(f"{images_dir.resolve().__str__()}/{now_str}.png", item)

    finally:
        stop.set()


class DatasetCollector(Task):
    def __init__(self, conf: DatasetCollectorConf):
        self.conf = conf

        self.ctx = get_context("spawn")
        self.stop_event: Event = self.ctx.Event()
        self.process: Process | None = None

    @staticmethod
    def run(conf: dict, stop: Event) -> None:
        conf_obj = DatasetCollectorConf.model_validate(conf)

        t_stop = TEvent()
        img_q = Queue(maxsize=8)
        detect_q = Queue(maxsize=8)

        threads = [
            Thread(target=reader_th, args=(img_q, t_stop, conf_obj.reader), daemon=False),
        ]
        if conf_obj.detection is not None:
            threads.append(Thread(target=detect_th, args=(img_q, detect_q, t_stop, conf_obj.detection), daemon=False))
            threads.append(Thread(target=writer_th, args=(detect_q, t_stop, conf_obj), daemon=False))

        else:
            threads.append(Thread(target=writer_th, args=(img_q, t_stop, conf_obj), daemon=False))

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
            name="record_worker"
        )
        self.process.start()

    def stop(self) -> None:
        if not self.process:
            return

        self.stop_event.set()
        self.process.join(5)
        if self.process.is_alive():
            self.process.terminate()
