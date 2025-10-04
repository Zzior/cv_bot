from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb

async def to_main_menu(message: Message, state: FSMContext, send_msg: str = None) -> None:
    await state.clear()
    await message.answer(send_msg if send_msg else "🏠 Main menu", reply_markup=main_rkb)
    await state.set_state(BotState.main_menu)
