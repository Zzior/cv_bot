from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CAMERAS_BT = "📷 Cameras"
WEIGHTS_BT = "⚖️ Weights"
RECORDS_BT = "🔴 Records"
INFERENCE_BT = "🔮 Inference"
TRAIN_BT = "🚂 Train"
SETTINGS_BT = "⚙️ Settings"

main_rkb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=CAMERAS_BT), KeyboardButton(text=WEIGHTS_BT)],
        [KeyboardButton(text=RECORDS_BT), KeyboardButton(text=INFERENCE_BT)],
        [KeyboardButton(text=TRAIN_BT), KeyboardButton(text=SETTINGS_BT)]
    ],
    resize_keyboard=True
)