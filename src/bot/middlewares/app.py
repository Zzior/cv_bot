from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware, types

from src.app import App

class AppMiddleware(BaseMiddleware):
    def __init__(self, app: App):
        self.app = app

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.update.Update,
            data: Dict[str, Any],
    ) -> Any:
        data["app"] = self.app
        return await handler(event, data)