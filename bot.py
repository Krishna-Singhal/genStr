import os
import asyncio
import json
from typing import Dict, Optional, List

from heroku3 import from_key
from pymongo import MongoClient
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
    DB_URI = os.environ.get("DB_URI", None)


class Bot(Client):
    database = MongoClient(Config.DB_URI)['genStr']

    def __init__(self):
        kwargs = {
            'api_id': Config.API_ID,
            'api_hash': Config.API_HASH,
            'session_name': ':memory:',
            'bot_token': Config.BOT_TOKEN
        }
        super().__init__(**kwargs)

    def get_collection(self, name: str):
        return self.database['name']

    async def start(self):
        await super().start()

    async def stop(self):
        await super().stop()

    
