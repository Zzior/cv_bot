import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from ..states import BotState
from ..keyboards import back_rkb, task_rkb
from ..navigation import to_main_menu, to_records, choose_camera

from services.record.conf import RecordConf
from services.base.video_reader.conf import VideoReaderConf
from services.base.video_writer.conf import VideoWriterConf

from app import App
from i18n.types import Translator

record_router = Router(name="record")


@record_router.message(BotState.records_list)
async def records_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["records"]:
        await state.set_data({"task_id": int(message.text)})
        await state.set_state(BotState.task)
        await message.answer(t("choose", lang), reply_markup=task_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await choose_camera(message, state, t, lang, app, BotState.records_choose_camera, to_add_camera=False)

    else:
        await message.answer(t("choose", lang))


@record_router.message(BotState.records_choose_camera)
async def records_choose_camera_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_records(message, state, t, lang, app)

    elif message.text:
        data = await state.get_data()
        if message.text not in data["cameras"]:
            await state.update_data({"camera_name": message.text})
            await state.set_state(BotState.records_enter_start)
            await message.answer(t("records.enter_start_time", lang))
        else:
            await message.answer(t("cameras.exists", lang))
    else:
        await message.answer("❗️" + t("cameras.add_name", lang))
