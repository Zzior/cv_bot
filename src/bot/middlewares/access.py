from typing import Dict, Any, Awaitable, Callable, Sequence

from aiogram import BaseMiddleware, types


class AccessMiddleware(BaseMiddleware):
    def __init__(self, user_ids: Sequence[int]):
        self.user_ids = set(user_ids)

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.update.Update,
            data: Dict[str, Any],
    ) -> Any:
        if event.event.from_user.id in self.user_ids:
            return await handler(event, data)
        else:
            return None
