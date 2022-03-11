import os
import json
import time
import asyncio

from bot import Bot, Config
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

bot = Bot()

API_TEXT = """Hi {}
Welcome to Pyrogram's SESSION_STRING` generator Bot.

`Send your API_ID to Continue.`"""
HASH_TEXT = "`Send your API_HASH to Continue.`\n\nPress /cancel to Cancel."
PHONE_NUMBER_TEXT = (
    "`Now send your Phone number to Continue"
    " include Country code. eg. +13124562345`\n\n"
    "Press /cancel to Cancel."
)


@bot.on_message(filters.private & filters.command("start"))
async def genStr(bot: Bot, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        int(api.text)
    except Exception:
        await api.delete()
        await msg.reply("`API ID Invalid.`\nPress /start to create again.")
        return
    api_id = api.text
    await api.delete()
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    api_hash = hash.text
    await hash.delete()
    try:
        client = Client(":memory:", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /start to create again.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    await msg.reply("`Successfully Connected to you Client.`")
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            await client.disconnect()
            return
        phone = number.text
        await number.delete()
        confirm = await bot.ask(chat.id, f'`Is "{phone}" correct? (y/n):` \n\ntype: `y` (If Yes)\ntype: `n` (If No)')
        if await is_cancel(msg, confirm.text):
            await client.disconnect()
            return
        if "y" in confirm.text.lower():
            await confirm.delete()
            break
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"`you have floodwait of {e.x} Seconds`")
        return await bot.sleep(msg)
    except ApiIdInvalid:
        await msg.reply("`Api Id and Api Hash are Invalid.`\n\nPress /start to create again.")
        return await bot.sleep(msg)
    except PhoneNumberInvalid:
        await msg.reply("`your Phone Number is Invalid.`\n\nPress /start to create again.")
        return await bot.sleep(msg)
    try:
        otp = await bot.ask(
            chat.id, ("`An otp is sent to your phone number, "
                      "Please enter otp in\n`1 2 3 4 5` format.`\n\n"
                      "`If Bot not sending OTP then try` /restart `cmd and again` /start `the Bot.`\n"
                      "Press /cancel to Cancel."), timeout=300)
    except TimeoutError:
        await msg.reply("`Time limit reached of 5 min.\nPress /start to create again.`")
        return await bot.sleep(msg)
    if await is_cancel(msg, otp.text):
        return await client.disconnect()
    otp_code = otp.text
    await otp.delete()
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("`Invalid Code.`\n\nPress /start to create again.")
        return await bot.sleep(msg)
    except PhoneCodeExpired:
        await msg.reply("`Code is Expired.`\n\nPress /start to create again.")
        return await bot.sleep(msg)
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "`This account have two-step verification code.\nPlease enter your second factor authentication code.`\nPress /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 min.\n\nPress /start to create again.`")
            return await bot.sleep(msg)
        if await is_cancel(msg, two_step_code.text):
            return await client.disconnect()
        new_code = two_step_code.text
        await two_step_code.delete()
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return await bot.sleep(msg)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return await bot.sleep(msg)
    session_string = await client.export_session_string()
    await client.send_message("me", f"#PYROGRAM #SESSION_STRING\n\n```{session_string}```")

    text = "`String Session is Successfully Generated.\nClick on Button Below.`"
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Click Me", url=f"tg://openmessage?user_id={chat.id}")]]
    )
    await bot.send_message(chat.id, text, reply_markup=reply_markup)
    return await bot.sleep(msg)


@bot.on_message(filters.private & filters.user(1158855661) & filters.command("restart"))
async def restart(bot: Bot, msg: Message):
    await msg.reply('✅')
    return Config.HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def start(_, msg: Message):
    out = f"""
Hello {msg.from_user.mention}, this is Pyrogram Session String Generator Bot \
which gives you `SESSION_STRING` for your UserBot.

It needs `API_ID` , `API_HASH` , `PHONE_NUMBER` and `One time Verification Code` \
which will send to your `PHONE_NUMBER`.
you have to put `OTP` in `1 2 3 4 5` this format.

(C) Author: [Krishna Singhal](https://t.me/Krishna_Singhal) and \
[UsergeTeam](https://t.me/TheUserge)
Give a Star ⭐️ to [REPO](https://github.com/Krishna-Singhal/genStr) if you like this Bot.
"""
    await msg.reply(out, disable_web_page_preview=True)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("`Process Cancelled.`")
        return True
    return False


if __name__ == "__main__":
    bot.run()
