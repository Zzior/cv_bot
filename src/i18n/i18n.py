from typing import Any


class I18n:
    def __init__(self, translations: dict[str, dict[str, str]], default_language: str) -> None:
        self.translations = translations
        self.default_language = default_language
        self.languages: tuple[str, ...] = tuple(translations.keys())

    def get_text(self, key: str, language: str, **params: Any) -> str:
        try:
            text = self.translations[language][key]
        except KeyError:
            text = self.translations.get(self.default_language, {}).get(key, key)

        try:
            return text.format(**params)
        except (KeyError, AttributeError, TypeError, SyntaxError):
            return text