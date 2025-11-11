from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import BotState
from ..parsers import parse_date
from ..keyboards import back_rkb, task_rkb, now_rkb
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
        await state.set_data({"task_id": int(message.text), "back_to": "to_records"})
        await state.set_state(BotState.task)
        await message.answer(t("choose", lang), reply_markup=task_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await choose_camera(message, state, t, lang, app, BotState.records_choose_camera, to_add=False)

    else:
        await message.answer(t("choose", lang))


@record_router.message(BotState.records_choose_camera)
async def records_choose_camera_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_records(message, state, t, lang, app)

    elif message.text:
        data = await state.get_data()
        if message.text in data["cameras"]:
            await state.update_data({"camera_name": message.text})
            await state.set_state(BotState.records_enter_start)
            await message.answer(t("records.enter_start_time", lang), reply_markup=now_rkb(t, lang))
        else:
            await message.answer(t("choose_camera", lang))
    else:
        await message.answer(t("choose_camera", lang))


@record_router.message(BotState.records_enter_start)
async def records_enter_start_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await choose_camera(message, state, t, lang, app, BotState.records_choose_camera, to_add=False)

    elif message.text:
        now = datetime.now().astimezone(app.config.system.tzinfo)

        if message.text == t("b.now", lang):
            date = now
        else:
            date = parse_date(message.text, tz=app.config.system.tzinfo)

        if date:
            if date >= now:
                await state.update_data({"start_date": date.isoformat()})
                await state.set_state(BotState.records_enter_end)
                await message.answer(t("records.enter_end_time", lang), reply_markup=back_rkb(t, lang))

            else:
                await message.answer(t("time_cannot_be_past", lang))
        else:
            await message.answer(t("️incorrect_format", lang))
    else:
        await message.answer("❗️" + t("cameras.enter_source", lang))


@record_router.message(BotState.records_enter_end)
async def records_enter_end_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.records_enter_start)
        await message.answer(t("records.enter_start_time", lang))

    elif message.text:
        now = datetime.now().astimezone(app.config.system.tzinfo)
        date = parse_date(message.text, tz=app.config.system.tzinfo)
        if date:
            data = await state.get_data()
            start = datetime.fromisoformat(data["start_date"])
            if start >= date:
                await message.answer(t("end_cannot_be_less", lang))

            elif start < date > now:
                await state.update_data({"end_date": date.isoformat()})
                await state.set_state(BotState.records_enter_segment)
                await message.answer(t("records.enter_segment", lang))

            else:
                await message.answer(t("time_cannot_be_past", lang))

        else:
            await message.answer(t("️incorrect_format", lang))
    else:
        await message.answer("❗️" + t("cameras.enter_source", lang))


@record_router.message(BotState.records_enter_segment)
async def records_enter_end_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.records_enter_end)
        await message.answer(t("records.enter_end_time", lang))

    elif message.text and message.text.isdigit():
        data = await state.get_data()
        async with app.db.session() as db:
            camera = await db.camera.get_by_name(data["camera_name"])
            camera_source = camera.source
            camera_fps = camera.fps
        start = datetime.fromisoformat(data["start_date"])
        end = datetime.fromisoformat(data["end_date"])
        dir_name = f"{start.year}{start.month}{start.day}_{start.hour}{start.minute}{start.second}"
        segment_size = int(message.text)
        await app.task_manager.add_task(
            start=start,
            end=end,
            conf=RecordConf(
                reader=VideoReaderConf(source=camera_source),
                writer=VideoWriterConf(
                    fps=camera_fps,
                    save_dir=str(app.config.storage_dir / "Records" / dir_name),
                    timezone=app.config.system.time_zone,
                    segment_size=segment_size * 60
                )
            )
        )
        await message.answer(t("task.created", lang))
        await to_records(message, state, t, lang, app)

    else:
        await message.answer("❗️" + t("️incorrect_format", lang))