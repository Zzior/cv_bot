from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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


def back_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("b.back", lang))]],
        resize_keyboard=True
    )


def cameras_rkb(t: Translator, lang: str, cameras: list[str]) -> ReplyKeyboardMarkup:
    result = ReplyKeyboardBuilder()
    result.add(KeyboardButton(text=t("b.add", lang)))

    for camera in cameras:
        result.add(KeyboardButton(text=camera))

    result.add(KeyboardButton(text=t("b.back", lang)))

    result.adjust(2)
    return result.as_markup(resize_keyboard=True)
