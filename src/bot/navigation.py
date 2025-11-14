from aiogram.fsm.context import FSMContext, StateType
from aiogram.types import Message

from .states import BotState
from .keyboards import main_rkb, build_rkb, back_rkb

from services.record.conf import RecordConf
from services.inference.conf import InferenceConf
from services.dataset_collector.conf import DatasetCollectorConf

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
        to_state: StateType, to_add: bool = False
) -> None:

    async with app.db.session() as db:
        cameras = await db.camera.all()
        cameras_info = {camera.name: camera.id for camera in cameras}

    await state.update_data({"cameras": cameras_info})
    if cameras_info:
        await state.set_state(to_state)
        await message.answer(t("choose_camera", lang), reply_markup=build_rkb(t, lang, cameras_info.keys()))

    else:
        await message.answer(t("cameras.empty", lang))
        if to_add:
            await state.set_state(BotState.cameras_add_name)
            await message.answer(t("cameras.enter_name", lang), reply_markup=back_rkb(t, lang))


async def to_weights(message: Message, state: FSMContext, t: Translator, lang: str, app: App, msg: str = None) -> None:
    async with app.db.session() as db:
        weights = await db.weight.all()
        weights_info = {weight.name: weight.id for weight in weights}

    if msg is None:
        if weights_info:
            msg = t("choose", lang)
        else:
            msg = t("weights.empty", lang)

    await state.set_state(BotState.weights_list)
    await state.set_data({"weights": weights_info})
    await message.answer(msg, reply_markup=build_rkb(t, lang, weights_info.keys(), add=True))


async def choose_weights(
        message: Message, state: FSMContext, t: Translator, lang: str, app: App,
        to_state: StateType, to_add: bool = False
) -> None:

    async with app.db.session() as db:
        weights = await db.weight.all()
        weights_info = {weight.name: weight.id for weight in weights}

    await state.update_data({"weights": weights_info})
    if weights_info:
        await state.set_state(to_state)
        await message.answer(t("choose_weights", lang), reply_markup=build_rkb(t, lang, weights_info.keys()))

    else:
        await message.answer(t("weights.empty", lang))
        if to_add:
            await state.set_state(BotState.cameras_add_name)
            await message.answer(t("weights.enter_name", lang), reply_markup=back_rkb(t, lang))


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
                ) + "————————————\n"
        else:
            msg = msg[:msg.rindex("————————————")]
    else:
        msg = t("choose", lang)

    await state.set_data({"records": tasks_ids})
    await state.set_state(BotState.records_list)
    await message.answer(msg, reply_markup=build_rkb(t, lang, tasks_ids, adjust=3, add=True))


async def to_inferences(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    time_zone = app.config.system.tzinfo
    msg = ""
    tasks_ids = []

    inferences = app.task_manager.get_tasks(task_type=InferenceConf.model_fields["kind"].default)
    if inferences:
        for inference in inferences:
            tasks_ids.append(str(inference.task_id))
            async with app.db.session() as db:
                camera = await db.camera.get_by_source(inference.conf.reader.source)
                weights = await db.weight.get_by_path(inference.conf.detection.weights_path)
                msg += t(
                    "inferences.info_frm", lang,
                    id=inference.task_id, camera_name=camera.name,
                    weights=weights.name,
                    start=inference.start_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S"),
                    end=inference.end_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S")
                ) + "————————————\n"
        else:
            msg = msg[:msg.rindex("————————————")]
    else:
        msg = t("choose", lang)

    await state.set_data({"inferences": tasks_ids})
    await state.set_state(BotState.inferences_list)
    await message.answer(msg, reply_markup=build_rkb(t, lang, tasks_ids, adjust=3, add=True))


async def to_datasets(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    time_zone = app.config.system.tzinfo
    msg = ""
    tasks_ids = []

    tasks = app.task_manager.get_tasks(task_type=DatasetCollectorConf.model_fields["kind"].default)
    if tasks:
        for task in tasks:
            tasks_ids.append(str(task.task_id))
            async with app.db.session() as db:
                camera = await db.camera.get_by_source(task.conf.reader.source)
                if task.conf.detection:
                    weights = await db.weight.get_by_path(task.conf.detection.weights_path)
                    weights_name = weights.name
                else:
                    weights_name = "None"

                msg += t(
                    "datasets.info_frm", lang,
                    id=task.task_id, camera_name=camera.name,
                    weights=weights_name,
                    start=task.start_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S"),
                    end=task.end_time.astimezone(time_zone).strftime("%Y.%m.%d %H:%M:%S")
                ) + "————————————\n"

        else:
            msg = msg[:msg.rindex("————————————")]
    else:
        msg = t("choose", lang)

    await state.set_data({"datasets": tasks_ids})
    await state.set_state(BotState.datasets_list)
    await message.answer(msg, reply_markup=build_rkb(t, lang, tasks_ids, adjust=3, add=True))


async def to_params(
        message: Message, state: FSMContext, t, lang: str,
        back_state: StateType, access_params: list[str]
) -> None:
    access_texts = []
    for a_param in access_params:
        access_texts.append(t(a_param, lang))

    await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, access_texts))
    await state.update_data({"access_params": access_texts, "back_state": back_state.state})
