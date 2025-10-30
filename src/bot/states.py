from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    main_menu = State()

    camera = State()
    cameras_list = State()
    cameras_add_name = State()
    cameras_add_source = State()
    cameras_add_fps = State()

    task = State()

    records_list = State()
    records_choose_camera = State()
    records_enter_start = State()
    records_enter_end = State()
    records_enter_segment = State()
