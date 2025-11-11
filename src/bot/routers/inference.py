from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import BotState
from ..parsers import parse_date
from ..keyboards import back_rkb, task_rkb, now_rkb
from ..navigation import to_main_menu, to_inferences, choose_camera

from services.inference.conf import InferenceConf
from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf

from app import App
from i18n.types import Translator

inference_router = Router(name="inference")


@inference_router.message(BotState.inferences_list)
async def inferences_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["inferences"]:
        await state.set_data({"task_id": int(message.text), "back_to": "to_inferences"})
        await state.set_state(BotState.task)
        await message.answer(t("choose", lang), reply_markup=task_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await choose_camera(message, state, t, lang, app, BotState.inferences_choose_camera, to_add=False)

    else:
        await message.answer(t("choose", lang))