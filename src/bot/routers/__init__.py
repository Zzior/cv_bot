from .commands import commands_router
from .other import other_router
from .menu import menu_router


routers = (
    commands_router,                        # First priority  Commands
    menu_router,                            # Routers
    other_router                            # Last priority
)
