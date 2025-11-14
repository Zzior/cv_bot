from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..states import BotState
from ..navigation import choose_weights
from ..keyboards import back_rkb, build_rkb, confirm_params_rkb, true_false_rkb

from app import App
from i18n.types import Translator

params_router = Router(name="params")


@params_router.message(BotState.params)
async def params_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()
    access_params = data["access_params"]

    if message.text == t("b.back", lang):
        await message.answer(t("choose", lang), reply_markup=confirm_params_rkb(t, lang))
        await state.set_state(data["back_state"])

    elif message.text not in access_params:
        await message.answer(t("choose", lang))
        return

    elif message.text == t("b.skip_frames", lang):
        await message.answer(t("p.skip_frames", lang), reply_markup=back_rkb(t, lang))
        await state.set_state(BotState.p_skip_frames)

    elif message.text == t("b.use_roi", lang):
        await message.answer(t("choose", lang), reply_markup=true_false_rkb(t, lang))
        await state.set_state(BotState.p_use_roi)

    elif message.text == t("b.classes", lang):
        await message.answer(t("p.TODO", lang))
        # await state.set_state(BotState.p_classes)

    elif message.text == t("b.confidence", lang):
        await message.answer(t("p.TODO", lang))
        # await state.set_state(BotState.p_confidence)

    elif message.text == t("b.iou", lang):
        await message.answer(t("p.TODO", lang))
        # await state.set_state(BotState.p_iou)

    elif message.text == t("b.weights", lang):
        await choose_weights(message, state, t, lang, app, BotState.p_weights, to_add=False)

    elif message.text == t("b.cls_conf", lang):
        await message.answer(t("p.TODO", lang))
        # await state.set_state(BotState.p_cls_conf)

    elif message.text == t("b.ignore_zone", lang):
        await message.answer(t("p.TODO", lang))
        # await state.set_state(BotState.p_ignore_zone)

@params_router.message(BotState.p_skip_frames)
async def p_skip_frames_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await state.set_state(BotState.params)
        await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text and message.text.isdigit():
        await state.update_data({"skip_frames": int(message.text)})
        await state.set_state(BotState.params)
        await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    else:
        await message.answer("❗️" + t("p.skip_frames", lang))


@params_router.message(BotState.p_use_roi)
async def p_use_roi_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await state.set_state(BotState.params)
        await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text == t("b.true", lang):
        await state.update_data({"use_roi": True})
        await state.set_state(BotState.params)
        await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text == t("b.false", lang):
        await state.update_data({"use_roi": False})
        await state.set_state(BotState.params)
        await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    else:
        await message.answer("❗️" + t("p.skip_frames", lang))


@params_router.message(BotState.p_weights)
async def p_weights_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await state.set_state(BotState.params)
        await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text in data["weights"]:
        await state.update_data({"weights_name": message.text})
        await state.set_state(BotState.params)
        await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    else:
        await message.answer(t("choose_weights", lang))
