from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb, build_rkb

from services.record.conf import RecordConf

from app import App
from i18n.types import Translator

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
        cameras_info = {camera.name: camera.id for camera in cameras}

    if msg is None:
        if cameras_info:
            msg = t("choose", lang)
        else:
            msg = t("cameras.empty", lang)

    await state.set_state(BotState.cameras_list)
    await state.set_data({"cameras": cameras_info})
    await message.answer(msg, reply_markup=build_rkb(t, lang, cameras_info.keys()))
