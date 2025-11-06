from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove

from ..states import BotState
from ..navigation import to_main_menu, to_weights
from ..keyboards import back_rkb, weight_rkb, confirm_delete_rkb

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
