from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    main_menu = State()
