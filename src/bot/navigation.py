from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb

from src.i18n.types import Translator

async def to_main_menu(message: Message, state: FSMContext, t: Translator, lang: str, send_msg: str = None) -> None:
    await state.clear()
    await message.answer(
        send_msg if send_msg else t("menu", lang),
        reply_markup=main_rkb(t, lang),
    )
    await state.set_state(BotState.main_menu)
