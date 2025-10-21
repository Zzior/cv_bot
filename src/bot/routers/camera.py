from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..states import BotState
from ..keyboards import back_rkb
from ..navigation import to_main_menu, to_cameras

from src.services.camera import Camera

from src.app import App
from src.i18n.types import Translator

camera_router = Router(name="camera")


@camera_router.message(BotState.cameras)
async def cameras_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["cameras"]:
        await message.answer("TODO camera view")

    elif message.text == t("b.add", lang):
        await message.answer(t("cameras.add_name", lang), reply_markup=back_rkb(t, lang))
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
            await state.update_data({"name": message.text})
            await state.set_state(BotState.cameras_add_source)
            await message.answer(t("cameras.add_source", lang))
        else:
            await message.answer(t("cameras.exists", lang))
    else:
        await message.answer("❗️" + t("cameras.add_name", lang))


async def add_camera(name: str, source: str, app: App, t: Translator, lang: str) -> str:
    if not source.startswith(("rtsp://", "rtsps://", "http://", "https://")):
        return t("cameras.add_source_wrong", lang)

    async with app.db.session() as db:
        can_add = await db.camera.check_to_add(name, source)
        if not can_add:
            return t("cameras.exists", lang)

    camera = Camera(source)
    ping = await camera.ping()
    if not ping:
        return t("cameras.not_work", lang)

    async with app.db.session() as db:
        await db.camera.new(name, source)

    return t("cameras.added", lang)

@camera_router.message(BotState.cameras_add_source)
async def cameras_add_source_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await message.answer(t("cameras.add_name", lang))
        await state.set_state(BotState.cameras_add_name)

    elif message.text:
        data = await state.get_data()
        try:
            added_msg = await add_camera(data["name"], message.text, app, t, lang)
        except Exception as e:
            _ = e
            added_msg = t("cameras.add_error", lang)

        await to_cameras(message, state, t, lang, app, msg=added_msg)

    else:
        await message.answer("❗️" + t("cameras.add_source", lang))