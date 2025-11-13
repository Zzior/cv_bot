from .inference import inference_router
from .commands import commands_router
from .dataset import dataset_router
from .camera import camera_router
from .record import record_router
from .weight import weight_router
from .other import other_router
from .task import task_router
from .menu import menu_router


routers = (
    commands_router,                        # First priority  Commands
    menu_router, camera_router, record_router, task_router, weight_router, inference_router, dataset_router,
    other_router                            # Last priority
)
