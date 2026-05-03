#
# Copyright (C) 2021-2022 by EXUTeam@Github, < https://github.com/EXUTeam >.
# This file is part of < https://github.com/EXUTeam/EXUMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/EXUTeam/EXUMusic/blob/master/LICENSE >
#
# All rights reserved.

from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

from ..logging import LOGGER

LOGGER(__name__).info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_.Alone
    LOGGER(__name__).info("Connected to your Mongo Database.")
except:
    LOGGER(__name__).error("Failed to connect to your Mongo Database.")
    exit()
