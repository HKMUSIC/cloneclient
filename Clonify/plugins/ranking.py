from datetime import datetime, timedelta
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import matplotlib.pyplot as plt
import io


db = MongoClient().rankingdb
rank_collection = db.rankings

@app.on_message(filters.group & ~filters.bot)
async def count_message(client, message):
    chat_id = message.chat.id
    user = message.from_user
    username = user.first_name or "Unknown"
    user_id = user.id

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())

    user_data = rank_collection.find_one({"chat_id": chat_id, "user_id": user_id})

    if not user_data:
        rank_collection.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "username": username,
            "overall": 1,
            "today": 1,
            "week": 1,
            "last_message": today_str
        })
    else:
        last_msg_date = datetime.strptime(user_data.get("last_message", today_str), "%Y-%m-%d")
        updates = {"$inc": {"overall": 1}}
        # Reset today if new day
        if last_msg_date.date() != datetime.utcnow().date():
            updates["$set"] = {"today": 1}
        else:
            updates["$inc"]["today"] = 1
        # Reset week if new week
        if last_msg_date.isocalendar()[1] != datetime.utcnow().isocalendar()[1]:
            updates["$set"]["week"] = 1
        else:
            updates["$inc"]["week"] = 1

        updates["$set"]["last_message"] = today_str
        rank_collection.update_one({"chat_id": chat_id, "user_id": user_id}, updates)

@app.on_message(filters.command("rankings"))
async def show_rankings(client, message):
    chat_id = message.chat.id
    await send_leaderboard(client, message, chat_id, "overall")

async def send_leaderboard(client, message, chat_id, mode):
    top_users = list(rank_collection.find({"chat_id": chat_id}).sort(mode, -1).limit(10))

    if not top_users:
        await message.reply_text("No ranking data available yet!")
        return

    names = [u['username'] for u in top_users]
    scores = [u[mode] for u in top_users]

    plt.figure(figsize=(8, 5))
    plt.barh(names[::-1], scores[::-1], color='skyblue')
    plt.xlabel("Messages")
    plt.ylabel("Users")
    plt.title(f"Top 10 - {mode.capitalize()}")
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Overall", callback_data=f"rank_overall_{chat_id}"),
            InlineKeyboardButton("Today", callback_data=f"rank_today_{chat_id}"),
            InlineKeyboardButton("Week", callback_data=f"rank_week_{chat_id}")
        ]
    ])

    caption = f"🏆 **Leaderboard ({mode.capitalize()})**\n\n"
    for i, u in enumerate(top_users, start=1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        caption += f"{emoji} **{u['username']}** — `{u[mode]}` messages\n"
    caption += f"\n📊 Total messages: {sum(scores)}"

    await message.reply_photo(buffer, caption=caption, reply_markup=buttons)

@app.on_callback_query(filters.regex(r"rank_(overall|today|week)_(\d+)"))
async def rank_callback(client, callback_query):
    mode, chat_id = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
    await callback_query.message.delete()
    fake_msg = type('obj', (object,), {'chat': callback_query.message.chat, 'reply_photo': callback_query.message.reply_photo})
    await send_leaderboard(client, fake_msg, chat_id, mode)

