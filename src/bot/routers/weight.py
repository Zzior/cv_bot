import asyncio
from pathlib import Path
from typing import BinaryIO

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Document, BufferedInputFile

from ..states import BotState
from ..navigation import to_main_menu, to_weights
from ..keyboards import back_rkb, weight_rkb, confirm_delete_rkb


from services.weight import Weight

from app import App
from i18n.types import Translator

weight_router = Router(name="weight")


@weight_router.message(BotState.weights_list)
async def weights_list_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await to_main_menu(message, state, t, lang)

    elif message.text in data["weights"]:
        await state.set_data({"weight_id": data["weights"][message.text]})
        await state.set_state(BotState.weights)
        await message.answer(t("choose", lang), reply_markup=weight_rkb(t, lang))

    elif message.text == t("b.add", lang):
        await message.answer(t("weights.enter_name", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.weights_add_name)

    else:
        await message.answer(t("choose", lang))


@weight_router.message(BotState.weights_add_name)
async def weights_add_name_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_weights(message, state, t, lang, app)

    elif message.text:
        data = await state.get_data()
        if message.text not in data["weights"]:
            await state.update_data({"name": message.text})
            await state.set_state(BotState.weights_add_file)
            await message.answer(t("weights.send_file", lang))
        else:
            await message.answer(t("weights.exists", lang))
    else:
        await message.answer("❗️" + t("weights.enter_name", lang))


async def add_weight(name: str, document: Document, app: App, t: Translator, lang: str) -> str | None:
    weight_path = app.config.storage_dir / "Weights" / document.file_name
    if weight_path.exists():
        return t("weights.file_exists", lang)

    async with app.db.session() as db:
        weight_in_db = await db.weight.check_to_add(name, str(weight_path))
        if not weight_in_db:
            return t("weights.exists", lang)

    try:
        await app.bot.download(document.file_id, weight_path)
    except Exception as e:
        _ = e
        return t("download_error", lang)

    try:
        weight = Weight(weight_path)
        classes = weight.get_classes()
    except Exception as e:
        _ = e
        if weight_path.is_file():
            weight_path.unlink()

        return t("weights.unsupported", lang)

    async with app.db.session() as db:
        await db.weight.new(name, str(weight_path), classes)

    return None


@weight_router.message(BotState.weights_add_file)
async def weights_add_file_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await message.answer(t("weights.enter_name", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.weights_add_name)

    elif message.document:
        data = await state.get_data()
        try:
            await message.answer(t("loading", lang))
            error_msg = await add_weight(data["name"], message.document, app, t, lang)
        except Exception as e:
            _ = e
            error_msg = t("weights.add_error", lang)

        if error_msg is None:
            await to_weights(message, state, t, lang, app, msg=t("weights.added", lang))
        else:
            await message.answer(error_msg)
    else:
        await message.answer("❗️" + t("weights.send_file", lang))



@weight_router.message(BotState.weights)
async def weights_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await to_weights(message, state, t, lang, app)

    elif message.text == t("b.rename", lang):
        await message.answer(t("weights.enter_name", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.weights_change_name)

    elif message.text == t("b.delete", lang):
        await message.answer(t("sure_delete", lang), reply_markup=confirm_delete_rkb(t, lang))
        await state.set_state(BotState.weights_delete)

    elif message.text == t("b.test", lang):
        await state.set_state(BotState.weights_test)
        await state.update_data({"confidence": 0.25, "iou": 0.7})
        await message.answer(t("weights.send_photo", lang), reply_markup=back_rkb(t, lang))

    else:
        await message.answer(t("choose", lang))


@weight_router.message(BotState.weights_change_name)
async def weights_change_name_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.weights)
        await message.answer(t("choose", lang), reply_markup=weight_rkb(t, lang))

    elif message.text:
        data = await state.get_data()
        async with app.db.session() as db:
            exists = await db.weight.get_by_name(message.text)
            if exists:
                await message.answer(t("weights.exists", lang))
                return

            else:
                weight = await db.weight.get(data["weight_id"])
                weight.name = message.text

        await state.set_state(BotState.weights)
        await message.answer(t("changes_saved", lang), reply_markup=weight_rkb(t, lang))

    else:
        await message.answer(t("weights.enter_name", lang))


@weight_router.message(BotState.weights_delete)
async def weights_delete_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.weights)
        await message.answer(t("choose", lang), reply_markup=weight_rkb(t, lang))

    elif message.text == t("b.delete", lang):
        data = await state.get_data()
        async with app.db.session() as db:
            weight = await db.weight.get(data["weight_id"])
            await db.weight.delete(data["weight_id"])
            Path(weight.path).unlink()

        await to_weights(message, state, t, lang, app, msg=t("deleted", lang))

    else:
        await message.answer(t("choose", lang))


def test_weights(image: BinaryIO, weights_path: str | Path, confidence: float = 0.25, iou: float = 0.7) -> bytes | None:
    try:
        weights = Weight(weights_path, confidence=confidence, iou=iou)
        result = weights.detect(weights.to_numpy(image.read()))
        return weights.from_numpy(result)

    except Exception as e:
        _ = e
        return None

@weight_router.message(BotState.weights_test)
async def weights_test(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    if message.text == t("b.back", lang):
        await state.set_state(BotState.weights)
        await message.answer(t("choose", lang), reply_markup=weight_rkb(t, lang))

    elif message.photo:
        data = await state.get_data()
        await message.answer(t("loading", lang))
        try:
            photo = await app.bot.download(message.photo[-1].file_id)
            async with app.db.session() as db:
                weights_db = await db.weight.get(data["weight_id"])
                weights_path = weights_db.path

            result = await asyncio.to_thread(test_weights, photo, weights_path, )
            await message.answer_photo(BufferedInputFile(result, "picture.jpg"))

        except Exception as e:
            _ = e
            await message.answer(t("test_error", lang))

    else:
        await message.answer(t("weights.send_photo", lang))