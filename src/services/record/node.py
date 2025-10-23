from multiprocessing import Process, Event, get_context

from .conf import RecordConf

class Record:
    def __init__(self, params: RecordConf):
        self.params = params

        self.ctx = get_context('spawn')
        self.stop_event: Event = self.ctx.Event()
        self.process: Process | None = None

    @staticmethod
    def run(params: dict, stop: Event) -> None:
        from ..base.video_reader.node import VideoReader
        from ..base.video_writer.node import VideoWriter

        params_obj = RecordConf.model_validate(params)
        reader = VideoReader(params_obj.reader)
        writer = VideoWriter(params_obj.writer)

        for frame in reader.process():
            if stop.is_set():
                break

            writer.write(frame)

        reader.stop()
        writer.stop()

    def start(self) -> None:
        self.process = self.ctx.Process(
            target=self.run,
            args=(self.params.model_dump(), self.stop_event),
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
