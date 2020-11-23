import os
import asyncio 

from pyrogram import filters, Client
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get('BOT_TOKEN')
       
bot = Client(":memory:",
             api_id=Config.API_ID,
             api_hash=Config.API_HASH,
             bot_token=Config.BOT_TOKEN)

API = """Hi {}
Welcome to Userge's `HU_STRING_SESSION` generator Bot.

Send your API_ID to Continue."""
HASH = "Send your API_HASH to Continue."
PHONE_NUMBER = "Now send your Phone number to Continue."

@bot.on_message(filters.command("start")
async def genStr(msg: Message):
    chat = msg.chat
    await msg.reply(API)
    app_id = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
        try:
            app_id = int(app_id)
            await msg.reply(HASH)
        except Exception:
            await msg.reply("APP ID Invalid.")
            return
        api_hash = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
        if len(api_hash) >= 30:
            await msg.reply(PHONE_NUMBER)
        else:
            await msg.reply("API HASH Invalid.")
            return
        phone = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
        if not phone.startswith("+"):
            await msg.reply("Phone number Invalid.\nUse Country Code Before your Phone Number.")
        try:
            client = Client("my_account", api_id=app_id, api_hash=api_hash)
            await client.connect()
            code = await client.send_code(phone)
            await msg.reply("An otp is sent to your phone number, Please enter to Continue.")
        except Exception as e:
            await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
            return
        otp = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
        try:
            await client.sign_in(phone, code.phone_code_hash, code=otp)
        except BadRequest:
            await msg.reply("Invalid Code\nPress /start for create again.")
        except SessionPasswordNeeded:
            await bot.send_message(chat.id, "This account have two-step verification code.\nPlease enter your second factor authentication code.")
            new_code = (await bot.get_history(chat.id, limit=1, reverse=False))[0].text
            await client.check_password(password=new_code)
        except Exception as e:
            await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
            return
        try:
            session_string = client.session.save()
            await client.send_message("me", f"#USERGE #HU_STRING_SESSION\n\n```{session_string}```")
            return await bot.send_message(chat.id , "String Session is Successfully Sent to your Saves Messages")
        except Exception as e:
            await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
            return
            
