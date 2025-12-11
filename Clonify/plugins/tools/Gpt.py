import requests
from SHUKLAMUSIC import app
from pyrogram.enums import ChatAction
from pyrogram import filters
import base64
from os import getenv

API_KEY = getenv("AIzaSyDgA9H65XPvRTQkRhDvx1BcjDHtaBdwB08")

# NEW GOOGLE API ENDPOINTS (LATEST)
TEXT_MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
IMAGE_MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"

# Keywords that trigger image generation
IMAGE_KEYWORDS = [
    "image", "photo", "picture", "draw", "generate an image",
    "create an image", "make an image", "ai image", "create photo",
    "generate photo", "draw me", "make a picture", "image of", "picture of"
]


@app.on_message(
    filters.command(
        ["ai", "ask", "chatgpt", "gpt", "solve"],
        prefixes=["+", ".", "/", "-", "", "$", "#", "&"],
    )
)
async def ai_handler(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            return await message.reply_text("â Example:\n\n/ai create an image of a cute robot")

        query = message.text.split(" ", 1)[1]

        # Detect if image prompt
        is_image_prompt = any(kw in query.lower() for kw in IMAGE_KEYWORDS)

        # -------------------------------------------------------------------
        # 1) IMAGE GENERATION (gemini-2.5-flash-image)
        # -------------------------------------------------------------------
        if is_image_prompt:
            waiting = await message.reply_text("ðŸ–¼ Generating image... Please wait 4â€“6 seconds.")

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": query}
                        ]
                    }
                ]
            }

            response = requests.post(IMAGE_MODEL_URL, json=payload)

            if response.status_code != 200:
                return await waiting.edit_text(
                    f"â ERROR generating image\nStatus Code: {response.status_code}\nResponse: {response.text}"
                )

            data = response.json()

            try:
                # New output format
                img_base64 = data["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
                img_bytes = base64.b64decode(img_base64)

            except Exception as e:
                return await waiting.edit_text(
                    f"â ERROR: Invalid image response.\n{e}\n\nRaw data:\n{data}"
                )

            await bot.send_photo(
                chat_id=message.chat.id,
                photo=img_bytes,
                caption="âœ¨ **AI Generated Image**"
            )

            await waiting.delete()
            return

        # -------------------------------------------------------------------
        # 2) TEXT GENERATION (gemini-2.5-flash)
        # -------------------------------------------------------------------
        payload = {
            "contents": [
                {"parts": [{"text": query}]}
            ]
        }

        response = requests.post(TEXT_MODEL_URL, json=payload)

        if response.status_code != 200:
            return await message.reply_text(
                f"â ERROR: Google API failed.\nStatus Code: {response.status_code}\nResponse: {response.text}"
            )

        data = response.json()

        try:
            result = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return await message.reply_text(f"â ERROR: Invalid text response.\n{e}")

        await message.reply_text(result)

    except Exception as e:
        await message.reply_text(f"â ERROR: {e}")
        
