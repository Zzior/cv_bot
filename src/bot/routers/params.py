import json

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
        await to_cls_conf(message, state, t, lang, app)

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
async def p_weights_handler(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await state.set_state(BotState.params)
        await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text in data["weights"]:
        u_data: dict = {"weights_name": message.text}
        if data["back_state"] == BotState.datasets_confirm_params.state:
            cls_conf: dict[int, list[float]] = {}
            cls_name_to_id: dict[str, int] = {}

            async with app.db.session() as db:
                db_weights = await db.weight.get_by_name(message.text)
                for str_id_, name in db_weights.classes.items():
                    cls_conf[int(str_id_)] = [0.25, 0.99]
                    cls_name_to_id[name] = int(str_id_)
                    cls_name_to_id[str_id_] = int(str_id_)

            u_data["cls_conf"] = cls_conf
            u_data["cls_name_to_id"] = cls_name_to_id

        await state.update_data(u_data)
        await state.set_state(BotState.params)
        await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    else:
        await message.answer(t("choose_weights", lang))


async def to_cls_conf(message: Message, state: FSMContext, t: Translator, lang: str, app: App) -> None:
    data = await state.get_data()

    if data.get("weights_name"):
        async with app.db.session() as db:
            db_weights = await db.weight.get_by_name(data["weights_name"])
            weights_names = db_weights.classes

        example = ""
        for id_, val in data["cls_conf"].items():
            example += f"\n    \"{weights_names[str(id_)]}\": \\[{val[0]}, {val[1]}\\],"

        example = example[:-1] + "\n"
        await state.set_state(BotState.p_cls_conf)
        example_message = await message.answer(f"```json\n{{{example}}}```", parse_mode="MarkdownV2")
        await example_message.reply(t("p.cls_conf_info", lang), reply_markup=back_rkb(t, lang))

    else:
        await message.answer(t("p.select_weights", lang))


def validate_cls_conf(text: str, cls_name_to_id: dict[str, int]) -> dict[int, list[int]] | None:
    try:
        cls_conf = json.loads(text)
        result: dict[int, list[int]] = {}
        if not isinstance(cls_conf, dict):
            return None

        for name, value in cls_conf.items():
            if name not in cls_name_to_id:
                return None

            if not isinstance(value, list):
                return None

            if len(value) != 2:
                return None

            if not (isinstance(value[0], float) and isinstance(value[1], float)):
                return None

            result[cls_name_to_id[name]] = value

        return result

    except json.JSONDecodeError:
        return None


@params_router.message(BotState.p_cls_conf)
async def p_cls_conf_handler(message: Message, state: FSMContext, t: Translator, lang: str) -> None:
    data = await state.get_data()

    if message.text == t("b.back", lang):
        await state.set_state(BotState.params)
        await message.answer(t("choose", lang), reply_markup=build_rkb(t, lang, data["access_params"]))

    elif message.text:
        cls_conf = validate_cls_conf(message.text, data["cls_name_to_id"])
        if cls_conf:
            await state.update_data({"cls_conf": cls_conf})
            await state.set_state(BotState.params)
            await message.answer(t("p.changed", lang), reply_markup=build_rkb(t, lang, data["access_params"]))
        else:
            await message.answer(t("️incorrect_format", lang))
    else:
        await message.answer(t("️incorrect_format", lang))