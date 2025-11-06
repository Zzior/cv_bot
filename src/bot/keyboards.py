from collections.abc import Iterable

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from i18n.types import Translator


def main_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.cameras", lang)), KeyboardButton(text=t("b.weights", lang))],
            [KeyboardButton(text=t("b.records", lang)), KeyboardButton(text=t("b.inference", lang))],
            [KeyboardButton(text=t("b.dataset", lang)), KeyboardButton(text=t("b.settings", lang))]
        ],
        resize_keyboard=True
    )


def back_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("b.back", lang))]],
        resize_keyboard=True
    )


def confirm_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.confirm", lang)), KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )


def now_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("b.now", lang)), KeyboardButton(text=t("b.back", lang))]],
        resize_keyboard=True
    )


def confirm_delete_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.delete", lang)), KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )

def task_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.stop", lang))],
            [KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )


def build_rkb(
        t: Translator, lang: str, buttons: Iterable[str],
        adjust: int = 2, back: bool = True, add: bool = False
) -> ReplyKeyboardMarkup:

    result = ReplyKeyboardBuilder()

    if add:
        result.add(KeyboardButton(text=t("b.add", lang)))

    for button in buttons:
        result.add(KeyboardButton(text=button))

    if back:
        result.add(KeyboardButton(text=t("b.back", lang)))

    result.adjust(adjust)
    return result.as_markup(resize_keyboard=True)


def camera_fps_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.auto", lang)), KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )


def camera_roi_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("b.show_roi", lang)), KeyboardButton(text=t("b.back", lang))]
        ],
        resize_keyboard=True
    )


def camera_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("b.rename", lang)),
                KeyboardButton(text=t("b.source", lang)),
                KeyboardButton(text=t("b.delete", lang))
            ],
            [
                KeyboardButton(text=t("b.ping", lang)),
                KeyboardButton(text=t("b.roi", lang)),
                KeyboardButton(text=t("b.fps", lang))
            ],
            [
                KeyboardButton(text=t("b.picture", lang)),
                KeyboardButton(text=t("b.back", lang))
            ]
        ],
        resize_keyboard=True
    )

def weight_rkb(t: Translator, lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("b.rename", lang)),
                KeyboardButton(text=t("b.delete", lang))
            ],
            [
                KeyboardButton(text=t("b.test", lang)),
                KeyboardButton(text=t("b.back", lang)),
            ]
        ],
        resize_keyboard=True
    )