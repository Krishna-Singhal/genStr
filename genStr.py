import os
import asyncio 

from asyncio.exceptions import TimeoutError
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)
from pyromod import listen

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get('BOT_TOKEN')
       
bot = Client(":memory:",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN)

API = """Hi {}
Welcome to Userge's `HU_STRING_SESSION` generator Bot.

`Send your API_ID to Continue.`"""
HASH = "`Send your API_HASH to Continue.`\nPress /cancel to Cancel."
PHONE_NUMBER = "`Now send your Phone number to Continue.`\nPress /cancel to Cancel."

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api_id = (await bot.ask(chat.id, API.format(msg.from_user.mention))).text
    if await is_cancel(msg, api_id):
        return
    try:
        api_id = int(api_id)
    except Exception:
        await msg.reply("`API ID Invalid.`\nPress /start to create again.")
        return
    api_hash = (await bot.ask(chat.id, HASH)).text
    if await is_cancel(msg, api_hash):
        return
    if not len(api_hash) >= 30:
        await msg.reply("`API HASH Invalid.`\nPress /start to create again.")
        return
    while True:
        phone = (await bot.ask(chat.id, PHONE_NUMBER)).text
        if not phone:
            continue
        if await is_cancel(msg, phone):
            return
        confirm = (await bot.ask(chat.id, f'Is "{phone}" correct? (y/n): ')).text.lower()
        if await is_cancel(msg, confirm):
            return
        if confirm == "y":
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /start to create again.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
    except FloodWait as e:
        await msg.reply(f"`you have floodwait of {e.x} Seconds`")
        return
    except ApiIdInvalid:
        await msg.reply("`Api Id and Api Hash are Invalid.`\nPress /start to create again.")
        return
    except PhoneNumberInvalid:
        await msg.reply("`your Phone Number is Invalid.`\nPress /start to create again.")
        return
    try:
        otp = (await bot.ask(chat.id, "`An otp is sent to your phone number, Please enter otp in `1-2-3-4-5` format.`\nPress /cancel to Cancel.", timeout=300)).text
    except TimeoutError:
        await msg.reply("`Time limit reached of 5 min.\nPress /start to create again.`")
        return
    if await is_cancel(msg, otp):
        return
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=otp)
    except PhoneCodeInvalid:
        await msg.reply("`Invalid Code.`\nPress /start to create again.")
        return
    except PhoneCodeExpired:
        await msg.reply("`Code is Expired.`\nPress /start to create again.")
        return
    except SessionPasswordNeeded:
        try:
            new_code = (await bot.ask(
                            chat.id, 
                            "`This account have two-step verification code.\nPlease enter your second factor authentication code.`\nPress /cancel to Cancel.",
                            timeout=300
                        )
            ).text
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 min.\nPress /start to create again.`")
            return
        if await is_cancel(msg, new_code):
            return
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYROGRAM #HU_STRING_SESSION\n\n```{session_string}```")
        text = `String Session is Successfully Generated.\nClick on Button Below.`"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Click Me", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await msg.reply(text, reply_marup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("`Process Cancelled.`")
        return True
    return False

if __name__ == "__main__":
    bot.run()
