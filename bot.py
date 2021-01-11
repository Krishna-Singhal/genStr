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
    CHAT_ID = int(os.environ.get("CHAT_ID", 0))
    DATA_ID = int(os.environ.get("DATA_ID", 0))


class Bot(Client):
    spamdata: Dict[int, int] = {}

    def __init__(self):
        kwargs = {
            'api_id': Config.API_ID,
            'api_hash': Config.API_HASH,
            'session_name': ':memory:',
            'bot_token': Config.BOT_TOKEN
        }
        super().__init__(**kwargs)

    async def start(self):
        await super().start()
        await self.load_data()

    async def stop(self):
        await self.save_data()
        await super().stop()

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
                f"`{json.dumps(self.spamdata)}`",
                disable_web_page_preview=True
            )
        except MessageNotModified:
            pass
