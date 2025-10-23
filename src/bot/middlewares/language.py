from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware, types


from i18n.i18n import I18n

class LanguageMiddleware(BaseMiddleware):
    def __init__(self, i18n: I18n):
        self.i18n = i18n

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.update.Update,
            data: Dict[str, Any],
    ) -> Any:
        # TO DO add multilanguage

        data["t"] = self.i18n.get_text
        data["lang"] = self.i18n.default_language

        return await handler(event, data)