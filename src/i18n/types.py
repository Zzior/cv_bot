from typing import Protocol, Any

class Translator(Protocol):
    def __call__(self, key: str, language: str, /, **params: Any) -> str: ...
