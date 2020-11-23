import os
import asyncio 

from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

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
HASH = "`Send your API_HASH to Continue.`"
PHONE_NUMBER = "`Now send your Phone number to Continue.`"

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    await msg.reply(API.format(msg.from_user.mention))
    api_id = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
    try:
        api_id = int(api_id)
        await msg.reply(HASH)
    except Exception:
        await msg.reply("`API ID Invalid.`")
        return
    api_hash = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
    if len(api_hash) >= 30:
        await msg.reply(PHONE_NUMBER)
    else:
        await msg.reply("`API HASH Invalid.`")
        return
    phone = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
    if not phone.startswith("+"):
        await msg.reply("`Phone number Invalid.`\nUse Country Code Before your Phone Number.")
        return
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await msg.reply("`An otp is sent to your phone number, Please enter to Continue.`")
    except FloodWait as e:
        await msg.reply(f"`you have floodwait of {e.x} Seconds`")
        return
    except ApiIdInvalid:
        await msg.reply("`Api Id and Api Hash are Invalid.`")
        return
    except PhoneNumberInvalid:
        await msg.reply("`your Phone Number is Invalid.`")
        return
    otp = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
    try:
        await client.sign_in(phone, code.phone_code_hash, code=otp)
    except PhoneCodeInvalid:
        await msg.reply("`Invalid Code.`\nPress /start for create again.")
        return
    except PhoneCodeExpired:
        await msg.reply("`Code is Expired.`\nPress /start for create again.")
        return
    except SessionPasswordNeeded:
        await bot.send_message(chat.id, "`This account have two-step verification code.\nPlease enter your second factor authentication code.`")
        new_code = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
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
        await client.send_message("me", f"#USERGE #HU_STRING_SESSION\n\n```{session_string}```")
        await bot.send_message(
            chat.id, 
            text="`String Session is Successfully.\nClick on Button Below.`",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Click Me", url=f"tg://user?id={chat.id}")]]
            )
        )
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return

if __name__ == "__main__":
    bot.run()
