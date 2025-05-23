from aiogram import BaseMiddleware
from aiogram.types import Message, User
from typing import Callable, Awaitable, Any
from .core import SimpleT9n
from .context import ctx_aiogram_t9n_lang


class SimpleT9nMiddleware(BaseMiddleware):
    def __init__(self, t9n: SimpleT9n) -> None:
        self.t9n = t9n

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        event_from_user: User | None = data.get("event_from_user", None)
        if event_from_user is None or event_from_user.language_code is None:
            ctx_aiogram_t9n_lang.set(self.t9n.default_lang)
        elif event_from_user.language_code not in self.t9n.available_langs:
            ctx_aiogram_t9n_lang.set(self.t9n.default_lang)
        else:
            ctx_aiogram_t9n_lang.set(event_from_user.language_code)
        data["t9n"] = self.t9n
        data["lang"] = ctx_aiogram_t9n_lang.get()
        return await handler(event, data)
