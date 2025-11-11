from typing import Any
from threading import Event
from queue import Queue, Full, Empty


def q_get(q: Queue, stop: Event, timeout: float = 0.1) -> Any:
    while not stop.is_set():
        try:
            return q.get(timeout=timeout)
        except Empty:
            pass
        except (EOFError, OSError):
            return None

    return None


def q_put(q: Queue, item: Any, stop: Event, timeout: float = 0.1, drop_oldest=False) -> bool:
    while not stop.is_set():
        try:
            q.put(item, timeout=timeout)
            return True

        except Full:
            if drop_oldest:
                try:
                    q.get_nowait()
                except Empty:
                    pass

        except (EOFError, OSError):
            break

    return False