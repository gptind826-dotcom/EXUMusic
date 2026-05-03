#
# Copyright (C) 2021-2022 by EXUTeam@Github, < https://github.com/EXUTeam >.
#
# This file is part of < https://github.com/EXUTeam/EXUMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/EXUTeam/EXUMusic/blob/master/LICENSE >
#
# All rights reserved.


class AssistantErr(Exception):
    def __init__(self, errr: str):
        super().__init__(errr)
