import time, re
from config import BOT_USERNAME
from pyrogram.enums import MessageEntityType
from pyrogram import filters
from pyrogram.types import Message
from Clonify import app
from Clonify.core.readable_time import get_readable_time
from Clonify.core.afkdb import add_afk, is_afk, remove_afk

@app.on_message(filters.command(["afk", "brb"], prefixes=["/", "!"]))
async def active_afk(_, message: Message):
    if message.sender_chat:
        return
    user_id = message.from_user.id

    if len(message.command) == 1 and not message.reply_to_message:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(message.command) > 1 and not message.reply_to_message:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    else:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }

    await add_afk(user_id, details)
    await message.reply_text(f"{message.from_user.first_name} ɪs ɴᴏᴡ ᴀғᴋ!")

chat_watcher_group = 1

@app.on_message(
    ~filters.me & ~filters.bot & ~filters.via_bot,
    group=chat_watcher_group,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    msg = ""
    replied_user_id = 0

    # Ignore AFK check if command is /afk or /brb
    if message.text and message.text.split()[0].lower() not in ["/afk", f"/afk@{BOT_USERNAME}", "/brb", f"/brb@{BOT_USERNAME}"]:
        verifier, reasondb = await is_afk(userid)
        if verifier:
            await remove_afk(userid)
            try:
                afktype = reasondb["type"]
                timeafk = reasondb["time"]
                reasonafk = reasondb["reason"]
                seenago = get_readable_time((int(time.time() - timeafk)))
                if afktype == "text":
                    msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\n"
                if afktype == "text_reason":
                    msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
            except:
                msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\n"

    # Handle reply AFK detection
    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.first_name
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                afktype = reasondb["type"]
                timeafk = reasondb["time"]
                reasonafk = reasondb["reason"]
                seenago = get_readable_time((int(time.time() - timeafk)))
                if afktype == "text":
                    msg += f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n"
                if afktype == "text_reason":
                    msg += f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
        except:
            pass

    # Detect plain @username mentions in text
    if message.entities:
        text = message.text or message.caption or ""
        mentions = re.findall(r"@([_0-9a-zA-Z]+)", text)
        for mention in mentions:
            try:
                user = await app.get_users(mention)
                if user.id == userid:
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n"
                    if afktype == "text_reason":
                        msg += f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
            except:
                continue

    if msg != "":
        try:
            await message.reply_text(msg, disable_web_page_preview=True)
        except:
            return
