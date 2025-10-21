from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb, cameras_rkb

from src.app import App
from src.i18n.types import Translator

async def to_main_menu(message: Message, state: FSMContext, t: Translator, lang: str, send_msg: str = None) -> None:
    await state.clear()
    await message.answer(
        send_msg if send_msg else t("menu", lang),
        reply_markup=main_rkb(t, lang),
    )
    await state.set_state(BotState.main_menu)

async def to_cameras(message: Message, state: FSMContext, t: Translator, lang: str, app: App, msg: str = None) -> None:
    async with app.db.session() as db:
        cameras = await db.camera.all()
        cameras_name = [camera.name for camera in cameras]

    if msg is None:
        if cameras_name:
            msg = t("choose", lang)
        else:
            msg = t("cameras.empty", lang)

    await state.set_state(BotState.cameras)
    await state.set_data({"cameras": cameras_name})
    await message.answer(msg, reply_markup=cameras_rkb(t, lang, cameras_name))