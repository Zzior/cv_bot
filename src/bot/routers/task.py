from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..states import BotState
from ..navigation import to_main_menu, to_records, to_inferences, to_datasets


from app import App
from i18n.types import Translator

task_router = Router(name="task")


@task_router.message(BotState.task)
async def task_handler(
        message: Message, state: FSMContext, t: Translator, lang: str, app: App,
) -> None:
    data = await state.get_data()
    back_to: str = data.get("back_to")
    if back_to == "to_records":
        back_func = to_records

    elif back_to == "to_inferences":
        back_func = to_inferences

    elif back_to == "to_datasets":
        back_func = to_datasets

    else:
        back_func = to_main_menu

    if message.text == t("b.back", lang):
        await back_func(message, state, t, lang, app)

    elif message.text == t("b.stop", lang):
        await app.task_manager.stop_task(data["task_id"])
        await message.answer(t("task.canceled", lang))
        await back_func(message, state, t, lang, app)

    else:
        await message.answer(t("choose", lang))

