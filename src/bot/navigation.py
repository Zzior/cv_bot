from aiogram.fsm.context import FSMContext, StateType
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb, build_rkb, back_rkb

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
    await message.answer(msg, reply_markup=build_rkb(t, lang, cameras_info.keys(), add=True))


async def choose_camera(
        message: Message, state: FSMContext, t: Translator, lang: str, app: App,
        to_state: StateType, to_add_camera: bool = False
) -> None:

    async with app.db.session() as db:
        cameras = await db.camera.all()
        cameras_info = {camera.name: camera.id for camera in cameras}

    await state.set_data({"cameras": cameras_info})
    if cameras_info:
        await state.set_state(to_state)
        await message.answer(t("choose_camera", lang), reply_markup=build_rkb(t, lang, cameras_info.keys()))

    else:
        await message.answer(t("cameras.empty", lang))
        if to_add_camera:
            await state.set_state(BotState.cameras_add_name)
            await message.answer(t("cameras.add_name", lang), reply_markup=back_rkb(t, lang))


async def to_records(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    time_zone = app.config.system.tzinfo
    msg = ""
    tasks_ids = []

    records = app.task_manager.get_tasks(task_type=RecordConf.model_fields["kind"].default)
    if records:
        for record in records:
            tasks_ids.append(str(record.task_id))
            async with app.db.session() as db:
                camera = await db.camera.get_by_source(record.conf.reader.source)
                msg += t(
                    "records.info_frm", lang,
                    id=record.task_id, camera_name=camera.name,
                    start=record.start_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S"),
                    end=record.end_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S")
                )
    else:
        msg = t("choose", lang)

    await state.set_data({"records": tasks_ids})
    await state.set_state(BotState.records_list)
    await message.answer(msg, reply_markup=build_rkb(t, lang, tasks_ids, adjust=3, add=True))