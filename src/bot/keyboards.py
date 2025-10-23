from collections.abc import Iterable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from i18n.types import Translator


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


def cameras_list_rkb(t: Translator, lang: str, cameras: Iterable[str]) -> ReplyKeyboardMarkup:
    result = ReplyKeyboardBuilder()
    result.add(KeyboardButton(text=t("b.add", lang)))

    for camera in cameras:
        result.add(KeyboardButton(text=camera))

    result.add(KeyboardButton(text=t("b.back", lang)))

    result.adjust(2)
    return result.as_markup(resize_keyboard=True)


def camera_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.rename", lang)), KeyboardButton(text=t("b.source", lang))],
            [KeyboardButton(text=t("b.roi", lang)), KeyboardButton(text=t("b.picture", lang))],
            [KeyboardButton(text=t("b.ping", lang)), KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )