from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import BotState
from ..parsers import parse_date
from ..keyboards import back_rkb, task_rkb, now_rkb, confirm_params_rkb
from ..navigation import to_main_menu, to_datasets, choose_camera, to_params

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
        await state.update_data(
            {
                "use_roi": True,
                "skip_frames": 0
            }
        )
    else:
        await message.answer(t("choose", lang))


@dataset_router.message(BotState.datasets_choose_camera)
async def datasets_choose_camera_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_datasets(message, state, t, lang, app)

    elif message.text:
        data = await state.get_data()
        if message.text in data["cameras"]:
            await state.update_data({"camera_name": message.text})
            await state.set_state(BotState.datasets_enter_start)
            await message.answer(t("enter_start_time", lang), reply_markup=now_rkb(t, lang))

        else:
            await message.answer(t("choose_camera", lang))
    else:
        await message.answer(t("choose_camera", lang))


@dataset_router.message(BotState.datasets_enter_start)
async def datasets_enter_start_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await choose_camera(message, state, t, lang, app, BotState.datasets_choose_camera, to_add=False)

    elif message.text:
        now = datetime.now().astimezone(app.config.system.tzinfo)

        if message.text == t("b.now", lang):
            date = now
        else:
            date = parse_date(message.text, tz=app.config.system.tzinfo)

        if date:
            if date >= now:
                await state.update_data({"start_date": date.isoformat()})
                await state.set_state(BotState.datasets_enter_end)
                await message.answer(t("enter_end_time", lang), reply_markup=back_rkb(t, lang))

            else:
                await message.answer(t("time_cannot_be_past", lang))
        else:
            await message.answer(t("️incorrect_format", lang))
    else:
        await message.answer("❗️" + t("enter_start_time", lang))


@dataset_router.message(BotState.datasets_enter_end)
async def datasets_enter_end_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.datasets_enter_start)
        await message.answer(t("enter_start_time", lang))

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
                await state.set_state(BotState.datasets_confirm_params)
                await message.answer(t("confirm_parameters", lang), reply_markup=confirm_params_rkb(t, lang))

            else:
                await message.answer(t("time_cannot_be_past", lang))

        else:
            await message.answer(t("️incorrect_format", lang))
    else:
        await message.answer("❗️" + t("enter_end_time", lang))


async def get_reader(data: dict, app: App) -> VideoReaderConf:
    async with app.db.session() as db:
        camera = await db.camera.get_by_name(data["camera_name"])
        camera_source = camera.source
        camera_roi = camera.roi

    return VideoReaderConf(
        source=camera_source,
        roi=camera_roi if data["use_roi"] else [],
        skip_frames=data["skip_frames"],
    )

async def get_detector(data: dict, app: App) -> DetectionConf | None:
    if data["weights_name"] and ["cls_conf"]:
        async with app.db.session() as db:
            weights = await db.weight.get_by_name(data["weights_name"])
            weights_path = weights.path

        minimal_conf = 1.0
        classes = []
        for cls, val in data["cls_conf"].items():
            classes.append(cls)

            if val[0] < minimal_conf:
                minimal_conf = val[0]

        return DetectionConf(
            weights_path=weights_path,
            classes=classes,
            confidence=minimal_conf,
            iou=data.get("iou") or DetectionConf.model_fields["iou"].default
        )
    else:
        return None

@dataset_router.message(BotState.datasets_confirm_params)
async def datasets_confirm_params_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.datasets_enter_end)
        await message.answer(t("enter_end_time", lang), reply_markup=back_rkb(t, lang))

    elif message.text == t("b.parameters", lang):
        await state.set_state(BotState.params)
        await to_params(
            message, state, t, lang,
            BotState.datasets_confirm_params,
            access_params=["b.skip_frames", "b.use_roi", "b.weights", "b.cls_conf", "b.iou", "b.ignore_zone"]
        )

    elif message.text == t("b.confirm", lang):
        data = await state.get_data()

        start = datetime.fromisoformat(data["start_date"])
        end = datetime.fromisoformat(data["end_date"])
        dir_name = start.strftime("%Y%m%d_%H%M%S")

        reader = await get_reader(data, app)
        detection = await get_detector(data, app)

        await app.task_manager.add_task(
            start=start,
            end=end,
            conf=DatasetCollectorConf(
                save_dir=str(app.config.storage_dir / "Datasets" / dir_name),
                reader=reader,
                detection=detection,
                classes_conf=data.get("cls_conf") or {},
                ignore_zone_ratio=data.get("ignore_zone_ratio") or DatasetCollectorConf.model_fields["ignore_zone_ratio"].default,
            )
        )
        await message.answer(t("task.created", lang))
        await to_datasets(message, state, t, lang, app)

    else:
        await message.answer(t("choose", lang))
