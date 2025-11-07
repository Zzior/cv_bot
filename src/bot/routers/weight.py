from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Document, BufferedInputFile, ReplyKeyboardRemove

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
        await state.set_state(BotState.weight)
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
        return t("weights.download_error", lang)

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
