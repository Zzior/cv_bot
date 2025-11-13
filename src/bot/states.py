from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    main_menu = State()

    camera = State()
    cameras_list = State()
    cameras_add_name = State()
    cameras_add_source = State()
    cameras_add_fps = State()

    camera_delete = State()
    camera_change_name = State()
    camera_change_source = State()
    camera_change_roi = State()
    camera_confirm_change_roi = State()
    camera_change_fps = State()

    weights = State()
    weights_list = State()
    weights_add_name = State()
    weights_add_file = State()
    weights_change_name = State()
    weights_delete = State()
    weights_test = State()

    task = State()

    records_list = State()
    records_choose_camera = State()
    records_enter_start = State()
    records_enter_end = State()
    records_enter_segment = State()

    inferences_list = State()
    inferences_choose_camera = State()
    inferences_choose_weights = State()
    inferences_enter_start = State()
    inferences_enter_end = State()
    inferences_enter_segment = State()

    datasets_list = State()
    datasets_choose_camera = State()
