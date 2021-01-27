import os
import json
from typing import Dict, Optional, List

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
    SPAMMERS_ID = int(os.environ.get("SPAMMERS_ID", 0))


class Bot(Client):
    spamdata: Dict[int, int] = {}
    spammers_dict: Dict[str, List[int]] = {}
    spammers: List[int] = []

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
        self.spammers = self.spammers_dict.get('spammers')

    async def stop(self):
        self.spammers_dict['spammers'] = self.spammers
        await self.save_data()
        await super().stop()

    async def load_data(self) -> None:
        msg = await self.get_messages(
            Config.CHAT_ID, Config.DATA_ID)
        if msg:
            self.spamdata = json.loads(msg.text)
        _msg = await self.get_messages(
            Config.CHAT_ID, Config.SPAMMERS_ID)
        if msg:
            self.spammers_dict = json.loads(_msg.text)

    async def save_data(self) -> None:
        try:
            await self.edit_message_text(
                Config.CHAT_ID,
                Config.DATA_ID,
                f"`{json.dumps(self.spamdata)}`",
                disable_web_page_preview=True
            )
            self.spammers_dict['spammers'] = self.spammers
            await self.edit_message_text(
                Config.CHAT_ID,
                Config.SPAMMERS_ID,
                f"`{json.dumps(self.spammers_dict)}`",
                disable_web_page_preview=True
            )
        except MessageNotModified:
            pass
