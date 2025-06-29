from config import Config, Txt
from helper.database import DARKXSIDE78
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os, sys, time, asyncio, logging, datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import html
import pytz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ADMIN_USER_ID = Config.ADMIN
PREMIUM_USERS_PER_PAGE = Config.PREMIUM_USERS_PER_PAGE
is_restarting = False

@Client.on_message(filters.command(["listpremium", "premium_users", "premiumusers"]) & filters.private)
async def list_premium_users(client, message):
    await send_premium_page(client, message, page=1)

@Client.on_callback_query(filters.regex(r"^premium_page:(\d+)$"))
async def premium_page_callback(client, callback_query):
    page = int(callback_query.data.split(":")[1])
    await send_premium_page(client, callback_query.message, page, callback_query)

async def send_premium_page(client, message, page=1, callback_query=None):
    total_premium = await DARKXSIDE78.col.count_documents({"is_premium": True})
    if total_premium == 0:
        text = "Nᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ғᴏᴜɴᴅ."
        if callback_query:
            await callback_query.answer("Nᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs.", show_alert=True)
            return await callback_query.message.edit_text(text)
        return await message.reply_text(text)

    pages = (total_premium + PREMIUM_USERS_PER_PAGE - 1) // PREMIUM_USERS_PER_PAGE
    page = max(1, min(page, pages))
    skip = (page - 1) * PREMIUM_USERS_PER_PAGE

    users = await DARKXSIDE78.col.find({"is_premium": True}).skip(skip).limit(PREMIUM_USERS_PER_PAGE).to_list(length=PREMIUM_USERS_PER_PAGE)

    lines = []
    for idx, user in enumerate(users, start=skip + 1):
        name = user.get("name") or user.get("first_name") or "N/A"
        username = user.get("username")
        user_id = user.get("_id")
        premium_expiry = user.get("premium_expiry")
        expiry_str = f" | Expires: {premium_expiry.strftime('%Y-%m-%d')}" if premium_expiry else ""
        line = f"{idx}. {name} ({'@'+username if username else user_id}){expiry_str}"
        lines.append(line)

    text = f"**Pʀᴇᴍɪᴜᴍ Usᴇʀs (Pᴀɢᴇ {page}/{pages}):**\n\n" + "\n".join(lines)

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("Bᴀᴄᴋ", callback_data=f"premium_page:{page-1}"))
    if page < pages:
        buttons.append(InlineKeyboardButton("Nᴇxᴛ", callback_data=f"premium_page:{page+1}"))

    markup = InlineKeyboardMarkup([buttons]) if buttons else None

    if callback_query:
        await callback_query.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
        await callback_query.answer()
    else:
        await message.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("restart") & filters.user(ADMIN_USER_ID))
async def restart_bot(b, m):
    global is_restarting
    if not is_restarting:
        is_restarting = True
        await m.reply_text(
            "**Aʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ?**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✓ Yᴇs", callback_data="confirm_restart"),
                 InlineKeyboardButton("✘ Nᴏ", callback_data="cancel_restart")]
            ])
        )

@Client.on_callback_query(filters.regex("confirm_restart"))
async def confirm_restart(bot: Client, callback_query):
    await callback_query.answer("Rᴇsᴛᴀʀᴛɪɴɢ...")
    await callback_query.message.delete()
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_callback_query(filters.regex("cancel_restart"))
async def cancel_restart(bot: Client, callback_query):
    global is_restarting
    is_restarting = False
    await callback_query.answer("Rᴇsᴛᴀʀᴛ Cᴀɴᴄᴇʟʟᴇᴅ!")
    await callback_query.message.delete()

@Client.on_message(filters.command("ban") & filters.user(Config.ADMIN))
async def ban_user(bot: Client, message: Message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return await message.reply_text("**Usᴀɢᴇ:** `/ban @username/userid [reason]`")
        
        user_ref = args[1]
        reason = args[2] if len(args) > 2 else "No reason provided"

        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        await DARKXSIDE78.col.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "ban_status.is_banned": True,
                "ban_status.banned_on": datetime.now(pytz.utc).isoformat(),
                "ban_status.ban_reason": reason
            }}
        )
        await message.reply_text(f"**🗸 Usᴇʀ {user['_id']} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.**\n**Rᴇᴀsᴏɴ:** {reason}")
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /ban @username/userid [reason]**")

@Client.on_message(filters.command("unban") & filters.user(Config.ADMIN))
async def unban_user(bot: Client, message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply_text("**Usᴀɢᴇ:** `/unban @username/userid`")
        
        user_ref = args[1]

        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        await DARKXSIDE78.col.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "ban_status.is_banned": False,
                "ban_status.banned_on": None,
                "ban_status.ban_reason": None
            }}
        )
        await message.reply_text(f"**🗸 Usᴇʀ {user['_id']} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.**")
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /unban @username/userid**")

@Client.on_message((filters.group | filters.private) & filters.command("leaderboard"))
async def leaderboard_handler(bot: Client, message: Message):
    try:
        user_id = message.from_user.id if message.from_user else None
        time_filter = "lifetime"

        async def generate_leaderboard(filter_type):
            pipeline = []
            match_stage = {}
            current_time = datetime.now()
            
            if filter_type == "today":
                start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                pipeline.append({"$match": {"rename_timestamp": {"$gte": start_time}}})
            elif filter_type == "week":
                days_since_monday = current_time.weekday()
                start_time = (current_time - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                pipeline.append({"$match": {"rename_timestamp": {"$gte": start_time}}})
            elif filter_type == "month":
                start_time = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                pipeline.append({"$match": {"rename_timestamp": {"$gte": start_time}}})
            elif filter_type == "year":
                start_time = current_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                pipeline.append({"$match": {"rename_timestamp": {"$gte": start_time}}})
            
            if filter_type != "lifetime":
                pipeline.extend([
                    {"$group": {
                        "_id": "$_id",
                        "rename_count": {"$sum": 1},
                        "first_name": {"$first": "$first_name"},
                        "username": {"$first": "$username"}
                    }}
                ])
            
            if pipeline:
                users = await DARKXSIDE78.col.aggregate(pipeline).sort("rename_count", -1).limit(10).to_list(10)
            else:
                users = await DARKXSIDE78.col.find().sort("rename_count", -1).limit(10).to_list(10)
            
            if not users:
                return None
            
            user_rank = None
            user_count = 0
            
            if user_id:
                if pipeline:
                    user_data = await DARKXSIDE78.col.aggregate(pipeline + [{"$match": {"_id": user_id}}]).to_list(1)
                    if user_data:
                        user_count = user_data[0].get("rename_count", 0)
                        higher_count = await DARKXSIDE78.col.aggregate(pipeline + [
                            {"$match": {"rename_count": {"$gt": user_count}}}
                        ]).count()
                        user_rank = higher_count + 1
                else:
                    user_data = await DARKXSIDE78.col.find_one({"_id": user_id})
                    if user_data:
                        user_count = user_data.get("rename_count", 0)
                        higher_count = await DARKXSIDE78.col.count_documents({"rename_count": {"$gt": user_count}})
                        user_rank = higher_count + 1
            
            filter_title = {
                "today": "Tᴏᴅᴀʏ's",
                "week": "Tʜɪs Wᴇᴇᴋ's",
                "month": "Tʜɪs Mᴏɴᴛʜ's",
                "year": "Tʜɪs Yᴇᴀʀ's",
                "lifetime": "Aʟʟ-Tɪᴍᴇ"
            }
            
            leaderboard = [f"<b>{filter_title[filter_type]} Tᴏᴘ 10 Rᴇɴᴀᴍᴇʀs</b>\n"]
            
            for idx, user in enumerate(users, 1):
                u_id = user['_id']
                count = user.get('rename_count', 0)
                
                try:
                    tg_user = await bot.get_users(u_id)
                    name = html.escape(tg_user.first_name or "Anonymous")
                    username = f"@{tg_user.username}" if tg_user.username else "No UN"
                except:
                    name = html.escape(user.get('first_name', 'Anonymous').strip())
                    username = f"@{user['username']}" if user.get('username') else "No UN"
                
                leaderboard.append(
                    f"{idx}. <b>{name}</b> "
                    f"(<code>{username}</code>) ➜ "
                    f"<i>{count} ʀᴇɴᴀᴍᴇs</i>"
                )
            
            if user_rank:
                leaderboard.append(f"\n<b>Yᴏᴜʀ Rᴀɴᴋ:</b> {user_rank} ᴡɪᴛʜ {user_count} ʀᴇɴᴀᴍᴇs")
            
            leaderboard.append(f"\nLᴀsᴛ ᴜᴘᴅᴀᴛᴇᴅ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            leaderboard.append(f"\n<i>**Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ {Config.LEADERBOARD_DELETE_TIMER} sᴇᴄᴏɴᴅs**</i>")
            
            return "\n".join(leaderboard)
        
        leaderboard_text = await generate_leaderboard("lifetime")
        
        if not leaderboard_text:
            no_data_msg = await message.reply_text("<blockquote>Nᴏ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ʏᴇᴛ!</blockquote>")
            await asyncio.sleep(10)
            await no_data_msg.delete()
            return
        
        sent_msg = await message.reply_text(leaderboard_text)
        
        @bot.on_callback_query(filters.regex("^lb_"))
        async def leaderboard_callback(client, callback_query):
            if callback_query.from_user.id != message.from_user.id:
                await callback_query.answer("Tʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ!", show_alert=True)
                return

            selected_filter = callback_query.data.split("_")[1]

            new_leaderboard = await generate_leaderboard(selected_filter)
            
            if not new_leaderboard:
                await callback_query.answer(f"Nᴏ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ {selected_filter} ғɪʟᴛᴇʀ", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                new_leaderboard,
                reply_markup=keyboard
            )
            
            await callback_query.answer()
        
        async def delete_messages():
            await asyncio.sleep(Config.LEADERBOARD_DELETE_TIMER)
            try:
                await sent_msg.delete()
            except:
                pass
            try:
                await message.delete()
            except:
                pass
        
        asyncio.create_task(delete_messages())
        
    except Exception as e:
        error_msg = await message.reply_text(
            "<b>Eʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ!</b>\n"
            f"<code>{str(e)}</code>\n\n"
            f"**Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ sᴇʟғ-ᴅᴇsᴛʀᴜᴄᴛ ɪɴ {Config.LEADERBOARD_DELETE_TIMER} sᴇᴄᴏɴᴅs.**"
        )
        await asyncio.sleep(Config.LEADERBOARD_DELETE_TIMER)
        await error_msg.delete()

@Client.on_message(filters.command("add_token") & filters.user(Config.ADMIN))
async def add_tokens(bot: Client, message: Message):
    try:
        _, amount, *user_info = message.text.split()
        user_ref = " ".join(user_info).strip()

        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        new_tokens = int(amount) + user.get('token', Config.DEFAULT_TOKEN)
        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {"token": new_tokens}}
        )
        await message.reply_text(f"**🗸 Aᴅᴅᴇᴅ {amount} ᴛᴏᴋᴇɴs ᴛᴏ ᴜsᴇʀ {user['_id']}. Nᴇᴡ ʙᴀʟᴀɴᴄᴇ: {new_tokens}**")
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /add_token <amount> @username/userid**")

@Client.on_message(filters.command("remove_token") & filters.user(Config.ADMIN))
async def remove_tokens(bot: Client, message: Message):
    try:
        _, amount, *user_info = message.text.split()
        user_ref = " ".join(user_info).strip()
        
        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        new_tokens = max(0, user.get('token', Config.DEFAULT_TOKEN) - int(amount))
        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {"token": new_tokens}}
        )
        await message.reply_text(f"**🗸 Rᴇᴍᴏᴠᴇᴅ {amount} ᴛᴏᴋᴇɴs ғʀᴏᴍ ᴜsᴇʀ {user['_id']}. Nᴇᴡ ʙᴀʟᴀɴᴄᴇ: {new_tokens}**")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /remove_token <amount> @username/userid")

@Client.on_message(filters.command("add_premium") & filters.user(Config.ADMIN))
async def add_premium(bot: Client, message: Message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            return await message.reply_text("**Usᴀɢᴇ: /add_premium @username/userid 1d (1h/1m/1y/lifetime)**")
        _, user_ref, duration = parts
        duration = duration.lower().strip()

        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})

        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")

        if duration in ["lifetime", "life", "forever"]:
            expiry = datetime(9999, 12, 31)
        else:
            import re
            match = re.match(r"(\d+)\s*(h|hour|hours|d|day|days|m|month|months|y|year|years)$", duration)
            if not match:
                return await message.reply_text("**Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ! Usᴇ 1d, 2days, 3m, 4months, 1y, 2years, lifetime, etc.**")
            num, unit = int(match.group(1)), match.group(2)
            if unit in ["h", "hour", "hours"]:
                delta = timedelta(hours=num)
            elif unit in ["d", "day", "days"]:
                delta = timedelta(days=num)
            elif unit in ["m", "month", "months"]:
                delta = timedelta(days=num * 30)
            elif unit in ["y", "year", "years"]:
                delta = timedelta(days=num * 365)
            else:
                return await message.reply_text("**Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ᴜɴɪᴛ!**")
            expiry = datetime.now() + delta

        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {
                "is_premium": True,
                "premium_expiry": expiry
            }}
        )
        await message.reply_text(f"**🗸 Pʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴜɴᴛɪʟ {expiry.strftime('%Y-%m-%d %H:%M:%S')}**")
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /add_premium @username/userid 1d (1h/1m/1y/lifetime)**")

@Client.on_message(filters.command("remove_premium") & filters.user(Config.ADMIN))
async def remove_premium(bot: Client, message: Message):
    try:
        _, user_ref = message.text.split(maxsplit=1)
        
        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {
                "is_premium": False,
                "premium_expiry": None
            }}
        )
        await message.reply_text("**🗸 Pʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʀᴇᴍᴏᴠᴇᴅ**")
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /remove_premium @username/userid**")


@Client.on_message(filters.private & filters.command("tutorial"))
async def tutorial(bot: Client, message: Message):
    user_id = message.from_user.id
    format_template = await DARKXSIDE78.get_format_template(user_id)
    await message.reply_text(
        text=Txt.FILE_NAME_TXT.format(format_template=format_template),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴏᴡɴᴇʀ", url=f"https://t.me/{Config.OWNER_USERNAME}"),
             InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=f"https://t.me/{Config.SUPPORT_CHANNEL_USERNAME}")]
        ])
    )


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await DARKXSIDE78.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))    
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇssɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟs.....**')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜs--** \n\n**Bᴏᴛ Uᴘᴛɪᴍᴇ:** {uptime} \n**Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ms` \n**Tᴏᴛᴀʟ Usᴇʀs:** `{total_users}`")

@Client.on_message(filters.command(["users", "user"]) & filters.user(Config.ADMIN))
async def get_users(bot, message):
    total_users = await DARKXSIDE78.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))    
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇssɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟs.....**')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜs--** \n\n**Tᴏᴛᴀʟ Usᴇʀs :** `{total_users}`")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} ʜᴀs Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bʀᴏᴀᴅᴄᴀsᴛ......")
    all_users = await DARKXSIDE78.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("**Bʀᴏᴀᴅᴄᴀsᴛ Sᴛᴀʀᴛᴇᴅ!!!**") 
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await DARKXSIDE78.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
           success += 1
        else:
           failed += 1
        if sts == 400:
           await DARKXSIDE78.delete_user(user['_id'])
        done += 1
        if not done % 20:
           await sts_msg.edit(f"**Bʀᴏᴀᴅᴄᴀsᴛ Iɴ Pʀᴏɢʀᴇss: \n\nTᴏᴛᴀʟ Usᴇʀs: {total_users} \nCᴏᴍᴘʟᴇᴛᴇᴅ: {done} / {total_users}\nSuccess: {success}\nFᴀɪʟᴇᴅ: {failed}**")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"**Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Usᴇʀs: {total_users}\nCᴏᴍᴘʟᴇᴛᴇᴅ: {done} / {total_users}\nSuccess: {success}\nFᴀɪʟᴇᴅ: {failed}**")
           
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Deactivated")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Blocked The Bot")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : User ID Invalid")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
