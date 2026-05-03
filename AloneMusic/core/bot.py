#
# Copyright (C) 2021-2022 by EXUTeam@Github, < https://github.com/EXUTeam >.
# This file is part of < https://github.com/EXUTeam/EXUMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/EXUTeam/EXUMusic/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import Client, errors
from pyrogram.enums import ParseMode

import config

from ..logging import LOGGER


class Alone(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            name="EXUMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b><u>\n\nɪᴅ : <code>{self.id}</code>\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except Exception as ex:
            LOGGER(__name__).warning(
                f"Bot could not post to log group ({type(ex).__name__}) — "
                "add the bot to your log group and make it admin to enable logging. Continuing anyway."
            )

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
