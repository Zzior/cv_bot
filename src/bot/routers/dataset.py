from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import BotState
from ..parsers import parse_date
from ..keyboards import back_rkb, task_rkb, now_rkb
from ..navigation import to_main_menu, to_datasets, choose_camera, choose_weights

from services.base.detection.conf import DetectionConf
from services.base.video_reader.conf import VideoReaderConf
from services.dataset_collector.conf import DatasetCollectorConf

from app import App
from i18n.types import Translator

dataset_router = Router(name="dataset")


@dataset_router.message(BotState.datasets_list)
async def datasets_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["datasets"]:
        await state.set_data({"task_id": int(message.text), "back_to": "to_datasets"})
        await state.set_state(BotState.task)
        await message.answer(t("choose", lang), reply_markup=task_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await choose_camera(message, state, t, lang, app, BotState.datasets_choose_camera, to_add=False)

    else:
        await message.answer(t("choose", lang))
