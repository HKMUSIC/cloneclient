import importlib
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Clonify import LOGGER, app, userbot
from Clonify.core.call import PRO
from Clonify.misc import sudo
from Clonify.plugins import ALL_MODULES
from Clonify.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from Clonify.plugins.tools.clone import restart_bots


async def main():
    if not config.STRING1:
        LOGGER(__name__).error("String Session not filled, please provide a valid session.")
        return

    await sudo()

    try:
        for user_id in await get_gbanned():
            BANNED_USERS.add(user_id)
        for user_id in await get_banned_users():
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    # ❌ DO NOT call app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("Clonify.plugins" + all_module)

    LOGGER("Clonify.plugins").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    await userbot.start()
    await PRO.start()

    try:
        await PRO.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("Clonify").error("START GROUP VOICE CHAT FIRST")
        return
    except Exception:
        pass

    await PRO.decorators()
    await restart_bots()

    LOGGER("Clonify").info("BOT STARTED SUCCESSFULLY")

    await idle()

    await userbot.stop()
    LOGGER("Clonify").info("BOT STOPPED")


if __name__ == "__main__":
    app.run(main())
