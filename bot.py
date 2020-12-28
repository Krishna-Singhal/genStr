import os
import json
from typing import Dict, Optional

from heroku3 import from_key
from pyrogram import Client
from pyromod import listen

from pyrogram.errors import MessageNotModified


class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", None)
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    APP_NAME = os.environ.get("APP_NAME", None)
    API_KEY = os.environ.get("API_KEY", None)
    HU_APP = from_key(API_KEY).apps()[APP_NAME]
    CHAT_ID = os.environ.get("CHAT_ID", None)
    DATA_ID = os.environ.get("DATA_ID", None)


class bot(Client):
    spamdata: Dict[int, int] = {}

    def __init__(self):
        super().__init__(
            ":memory:",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )

    async def load_data(self) -> None:
        msg = await self.get_messages(
            Config.CHAT_ID, Config.DATA_ID)
        if msg:
            self.spamdata = json.loads(msg.text)

    async def save_data(self) -> None:
        try:
            await self.edit_message_text(
                Config.CHAT_ID,
                Config.DATA_ID,
                json.dumps(self.spamdata),
                disable_web_page_preview=True
            )
        except MessageNotModified:
            pass
