from __future__ import annotations
from typing import TYPE_CHECKING
from contextvars import ContextVar

if TYPE_CHECKING:
    from .core import SimpleT9n


ctx_aiogram_t9n_lang: ContextVar[str] = ContextVar("aiogram_t9n_lang", default="en")
ctx_aiogram_t9n: ContextVar[SimpleT9n | None] = ContextVar("aiogram_t9n", default=None)


def get_t9n() -> SimpleT9n:
    t9n = ctx_aiogram_t9n.get()
    if t9n is None:
        raise LookupError("T9n context is not set")
    return t9n


def gettext(key: str, *args, **kwargs) -> str:
    try:
        return get_t9n().gettext(key, *args, **kwargs)
    except LookupError:
        return key
