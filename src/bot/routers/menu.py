from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states import BotState
from src.bot.navigation import to_cameras

from src.app import App
from src.i18n.types import Translator

menu_router = Router(name="user")


@menu_router.message(BotState.main_menu)
async def main_menu_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.cameras", lang):
        await to_cameras(message, state, t, lang, app)

    else:
        await message.answer(t("choose", lang))