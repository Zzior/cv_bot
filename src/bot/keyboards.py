from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.i18n.types import Translator


def main_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.cameras", lang)), KeyboardButton(text=t("b.weights", lang))],
            [KeyboardButton(text=t("b.records", lang)), KeyboardButton(text=t("b.inference", lang))],
            [KeyboardButton(text=t("b.train", lang)), KeyboardButton(text=t("b.settings", lang))]
        ],
        resize_keyboard=True
    )