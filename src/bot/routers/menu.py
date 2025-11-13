from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..states import BotState
from ..navigation import to_cameras, to_weights, to_records, to_inferences, to_datasets

from app import App
from i18n.types import Translator

menu_router = Router(name="user")


@menu_router.message(BotState.main_menu)
async def main_menu_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.cameras", lang):
        await to_cameras(message, state, t, lang, app)

    elif message.text == t("b.weights", lang):
        await to_weights(message, state, t, lang, app)

    elif message.text == t("b.records", lang):
        await to_records(message, state, t, lang, app)

    elif message.text == t("b.inference", lang):
        await to_inferences(message, state, t, lang, app)

    elif message.text == t("b.dataset", lang):
        await to_datasets(message, state, t, lang, app)

    elif message.text == t("b.settings", lang):
        await message.answer("TODO")

    else:
        await message.answer(t("choose", lang))