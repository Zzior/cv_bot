from typing import Sequence


def calc_c_point(bbox: list[int]) -> tuple[int, int]:
    return (
        (bbox[0] + bbox[2]) // 2,
        (bbox[1] + bbox[3]) // 2,
    )


def get_roi(shape: tuple[int, int], ratio: int):
    x_start = shape[0] * (ratio / 200)
    x_end = shape[0] - x_start
    y_start = shape[1] * (ratio / 200)
    y_end = shape[1] - y_start

    return [
        [x_start, y_start], [x_end, y_start],
        [x_end, y_end], [x_start, y_end],
    ]


def get_yolo_label(cls: int, detect_xyxy: Sequence[int], mov_size: Sequence[int]) -> str:
    x_min, y_min, x_max, y_max = detect_xyxy
    x_center = (x_min + x_max) / 2 / mov_size[0]
    y_center = (y_min + y_max) / 2 / mov_size[1]
    width = (x_max - x_min) / mov_size[0]
    height = (y_max - y_min) / mov_size[1]

    return f"{cls} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
