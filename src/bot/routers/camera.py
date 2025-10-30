import asyncio

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove

from ..states import BotState
from ..navigation import to_main_menu, to_cameras
from ..keyboards import back_rkb, camera_rkb, camera_fps_rkb, confirm_delete_rkb

from services.camera import Camera

from app import App
from i18n.types import Translator

camera_router = Router(name="camera")


@camera_router.message(BotState.cameras_list)
async def cameras_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["cameras"]:
        await state.set_data({"camera_id": data["cameras"][message.text]})
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await message.answer(t("cameras.enter_name", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.cameras_add_name)

    else:
        await message.answer(t("choose", lang))


@camera_router.message(BotState.cameras_add_name)
async def cameras_add_name_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_cameras(message, state, t, lang, app)

    elif message.text:
        data = await state.get_data()
        if message.text not in data["cameras"]:
            await state.set_data({"name": message.text})
            await state.set_state(BotState.cameras_add_source)
            await message.answer(t("cameras.enter_source", lang))
        else:
            await message.answer(t("cameras.exists", lang))
    else:
        await message.answer("❗️" + t("cameras.enter_name", lang))


async def check_source(source: str, t: Translator, lang: str) -> str | None:
    if not source.startswith(("rtsp://", "rtsps://", "http://", "https://")):
        return t("️incorrect_format", lang)

    camera = Camera(source)
    ping = await camera.ping()

    if not ping:
        return t("cameras.not_work", lang)

    return None

@camera_router.message(BotState.cameras_add_source)
async def cameras_add_source_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    if message.text == t("b.back", lang):
        await message.answer(t("cameras.enter_name", lang))
        await state.set_state(BotState.cameras_add_name)

    elif message.text:
        try:
            source_error = await check_source(message.text, t, lang)
        except Exception as e:
            _ = e
            source_error = t("cameras.check_error", lang)

        if source_error:
            await message.answer(source_error)

        else:
            await state.update_data({"source": message.text})
            await state.set_state(BotState.cameras_add_fps)
            await message.answer(t("cameras.add_fps", lang), reply_markup=camera_fps_rkb(t, lang))

    else:
        await message.answer("❗️" + t("cameras.enter_source", lang))


async def add_camera(name: str, source: str, fps: int, app: App, t: Translator, lang: str) -> str:
    try:
        async with app.db.session() as db:
            can_add = await db.camera.check_to_add(name, source)
            if not can_add:
                return t("cameras.exists", lang)

        async with app.db.session() as db:
            await db.camera.new(name, source, fps)

        return t("cameras.added", lang)

    except Exception as e:
        _ = e
        return t("cameras.add_error", lang)

@camera_router.message(BotState.cameras_add_fps)
async def cameras_add_fps_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await message.answer(t("cameras.enter_name", lang))
        await state.set_state(BotState.cameras_add_source)

    if message.text == t("b.auto", lang):
        camera = Camera(data["source"])
        await message.answer(t("cameras.detecting_fps", lang), reply_markup=ReplyKeyboardRemove())
        detected_fps = await asyncio.to_thread(camera.get_fps, calc_frames=60)
        if detected_fps is None:
            await message.answer(t("cameras.fps_detection_err", lang), reply_markup=camera_fps_rkb(t, lang))
        else:
            detected_fps = round(detected_fps)
            await message.answer(t("cameras.add_fps_detected", lang, fps=detected_fps))
            added_msg = await add_camera(data["name"], data["source"], detected_fps, app, t, lang)
            await to_cameras(message, state, t, lang, app, msg=added_msg)

    elif message.text and message.text.isdigit():
        added_msg = await add_camera(data["name"], data["source"], int(message.text), app, t, lang)
        await to_cameras(message, state, t, lang, app, msg=added_msg)

    else:
        await message.answer("❗️" + t("cameras.enter_source", lang))


@camera_router.message(BotState.camera)
async def camera_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_cameras(message, state, t, lang, app)

    elif message.text == t("b.rename", lang):
        await message.answer(t("cameras.enter_name", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.camera_change_name)

    elif message.text == t("b.source", lang):
        await message.answer(t("cameras.enter_source", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.camera_change_source)

    elif message.text == t("b.delete", lang):
        await message.answer(t("sure_delete", lang), reply_markup=confirm_delete_rkb(t, lang))
        await state.set_state(BotState.camera_delete)

    elif message.text == t("b.roi", lang):
        await message.answer("TODO")

    elif message.text == t("b.fps", lang):
        await message.answer("TODO")

    elif message.text == t("b.picture", lang):
        await camera_picture(message, state, t, lang, app)

    elif message.text == t("b.ping", lang):
        await camera_ping(message, state, t, lang, app)

    else:
        await message.answer(t("choose", lang))


async def camera_ping(message: Message, state: FSMContext, t: Translator, lang: str, app: App):
    data = await state.get_data()
    async with app.db.session() as db:
        camera = await db.camera.get(data["camera_id"])
        source = camera.source

    if await Camera(source).ping():
        await message.answer(t("cameras.pong", lang))
    else:
        await message.answer(t("cameras.ping_error", lang))

async def camera_picture(message: Message, state: FSMContext, t: Translator, lang: str, app: App):
    await message.answer(t("loading", lang))

    data = await state.get_data()
    async with app.db.session() as db:
        camera = await db.camera.get(data["camera_id"])
        source = camera.source

    camera = Camera(source)
    pic = await asyncio.to_thread(camera.picture)
    if pic:
        await message.answer_photo(BufferedInputFile(pic, "picture.jpg"))
    else:
        await message.answer(t("cameras.picture_error", lang))


@camera_router.message(BotState.camera_change_name)
async def camera_change_name_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))

    elif message.text:
        data = await state.get_data()
        async with app.db.session() as db:
            exists = await db.camera.get_by_name(message.text)
            if exists:
                await message.answer(t("cameras.exists", lang))
                return

            else:
                camera = await db.camera.get(data["camera_id"])
                camera.name = message.text

        await message.answer(t("changes_saved", lang))
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))

    else:
        await message.answer(t("cameras.enter_name", lang))


@camera_router.message(BotState.camera_change_source)
async def camera_change_name_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))

    elif message.text:
        data = await state.get_data()

        async with app.db.session() as db:
            exists = await db.camera.get_by_source(message.text)
            if exists:
                await message.answer(t("cameras.exists", lang))
                return

        source_error = await check_source(message.text, t, lang)
        if source_error:
            await message.answer(source_error)
            return

        async with app.db.session() as db:
            camera = await db.camera.get(data["camera_id"])
            camera.source = message.text

        await message.answer(t("changes_saved", lang))
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))
    else:
        await message.answer(t("cameras.enter_name", lang))


@camera_router.message(BotState.camera_delete)
async def camera_delete_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.camera)
        await message.answer(t("choose", lang), reply_markup=camera_rkb(t, lang))

    elif message.text:
        data = await state.get_data()
        async with app.db.session() as db:
            await db.camera.delete(data["camera_id"])

        await to_cameras(message, state, t, lang, app, msg=t("deleted", lang))

    else:
        await message.answer(t("cameras.enter_name", lang))