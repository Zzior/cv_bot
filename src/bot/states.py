from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    main_menu = State()

    cameras = State()
    cameras_add_name = State()
    cameras_add_source = State()
