import sys
import traceback
import asyncio
from functools import wraps

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from MissCutie import OWNER_ID, pbot


def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line

    result.append(small_msg)

    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            return
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            error_feedback = split_limits(
                "**ERROR** | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                    0 if not message.from_user else message.from_user.id,
                    0 if not message.chat else message.chat.id,
                    message.text or message.caption,
                    "".join(errors),
                ),
            )
            for x in error_feedback:
                await pbot.send_message(OWNER_ID, x)
            raise err

    return capture


def asyncify(func):
    async def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        func_out = await loop.run_in_executor(None, func, *args, **kwargs)
        return func_out

    return inner


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(func(*args, **kwargs))
        except Exception as e:
            LOGGER.error(
                f"Failed to create task for {func.__name__} : {e}"
            )  # skipcq: PYL-E0602

    return wrapper
