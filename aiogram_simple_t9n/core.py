from __future__ import annotations
from typing import TYPE_CHECKING
import json
from pathlib import Path
from .context import ctx_aiogram_t9n_lang
from functools import lru_cache

if TYPE_CHECKING:
    from .middleware import SimpleT9nMiddleware


class LangMessages:
    def __init__(self, messages: dict[str, str | list | dict]):
        self.messages = messages

    def get(self, key: str, sep: str = "\n") -> str:
        try:
            return self.get_from_dir(key, self.messages, sep)
        except (IndexError, KeyError, ValueError):
            return key

    def get_from_dir(self, key: str, current_dir: dict | list, sep: str) -> str:
        keys = key.split(".")
        current = current_dir

        for i, k in enumerate(keys):
            if isinstance(current, dict):
                current = current[k]
            elif isinstance(current, list):
                if i == len(keys) - 1 and k.isdigit():
                    return self.handle_list_element(current, int(k), sep)
                current = current[int(k)] if k.isdigit() else current
            else:
                raise IndexError("Key path mismatch")

        if isinstance(current, list):
            return sep.join(map(str, current))
        return str(current)

    def handle_list_element(self, lst: list, index: int, sep: str) -> str:
        try:
            element = lst[index]
            if isinstance(element, list):
                return sep.join(map(str, element))
            return str(element)
        except IndexError:
            return ""

    def __getitem__(self, key: str) -> str:
        return self.get(key)


class SimpleT9n:
    def __init__(
        self, default_lang: str = "en", translations_folder: str | Path = Path("lang")
    ):
        if isinstance(translations_folder, str):
            translations_folder = Path(translations_folder)

        if not translations_folder.exists():
            translations_folder.mkdir()

        self.default_lang = default_lang
        self.translations_folder = translations_folder
        self.langs = self.find_langs()

    @property
    def current_lang(self) -> str:
        return ctx_aiogram_t9n_lang.get()

    @current_lang.setter
    def current_lang(self, value: str) -> None:
        ctx_aiogram_t9n_lang.set(value)

    @property
    def available_langs(self) -> tuple:
        return tuple(self.langs.keys())

    @lru_cache(maxsize=None)
    def find_langs(self) -> dict[str, LangMessages]:
        langs = {}
        for file in self.translations_folder.glob("*.[jJ][sS][oO][nN]"):
            with file.open("r") as f:
                langs[file.stem] = LangMessages(json.load(f))
        return langs

    def gettext(self, key: str, *args, **kwargs) -> str:
        try:
            message = self.langs[self.current_lang].get(key)
        except KeyError:
            message = self.langs[self.default_lang].get(key)

        if not message:
            return f"Missing translation: {key}"

        return message.format(*args, **kwargs)

    def get_middleware(self) -> SimpleT9nMiddleware:
        return SimpleT9nMiddleware(self)
