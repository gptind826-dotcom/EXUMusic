#
# Copyright (C) 2021-2022 by EXUTeam@Github, < https://github.com/EXUTeam >.
# This file is part of < https://github.com/EXUTeam/EXUMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/EXUTeam/EXUMusic/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AloneMusic import LOGGER, app, userbot
from AloneMusic.core.call import Alone
from AloneMusic.misc import sudo
from AloneMusic.plugins import ALL_MODULES
from AloneMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("AloneMusic.plugins" + all_module)
    LOGGER("EXUMusic.plugins").info("Successfully Imported Modules...")

    # ── Write live bot info so the Flask dashboard can display real values ──
    import json as _json, os as _os
    _bot_info: dict = {
        "bot_name":     app.name.strip(),
        "bot_username": f"@{app.username}" if app.username else "",
        "bot_id":       app.id,
        "owner_id":     config.OWNER_ID,
        "owner_name":   "",
        "owner_username": "",
        "assistant_name":     "",
        "assistant_username": "",
    }
    try:
        _owner = await app.get_users(config.OWNER_ID)
        _bot_info["owner_name"]     = (_owner.first_name or "") + (" " + _owner.last_name if _owner.last_name else "")
        _bot_info["owner_username"] = f"@{_owner.username}" if _owner.username else str(config.OWNER_ID)
    except Exception:
        _bot_info["owner_username"] = str(config.OWNER_ID)
    _json.dump(_bot_info, open(_os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "bot_info.json"), "w"))

    try:
        await userbot.start()
        if hasattr(userbot, "one") and userbot.one and getattr(userbot.one, "name", None):
            _bot_info["assistant_name"]     = userbot.one.name
            _bot_info["assistant_username"] = f"@{userbot.one.username}" if getattr(userbot.one, "username", None) else ""
            _json.dump(_bot_info, open(_os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "bot_info.json"), "w"))
    except Exception as e:
        LOGGER("EXUMusic").warning(
            f"Assistant userbot failed to start: {e}\n"
            "Voice chat features will be disabled. Regenerate your STRING_SESSION using pyrofork."
        )
    try:
        await Alone.start()
    except Exception as e:
        LOGGER("EXUMusic").warning(f"PyTgCalls failed to start: {e}")
    try:
        await Alone.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("EXUMusic").warning(
            "Videochat not active in log group — voice chat test skipped."
        )
    except Exception:
        pass
    await Alone.decorators()
    LOGGER("EXUMusic").info(
        "EXU Music Bot started successfully — join @EXUTeam"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("EXUMusic").info("Stopping EXU Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
