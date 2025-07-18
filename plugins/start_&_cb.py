import random
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from datetime import datetime, timedelta
from helper.database import DARKXSIDE78
from config import *
from config import Config
from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from urllib.parse import quote
import string
from telegraph import upload_file
import logging
import pytz
from functools import wraps
import secrets
import logging
from plugins.extra.fonts import FONTS, apply_font
#from plugins.ai import *
# Add this at the top of your file with other imports
from typing import Dict, Optional



def check_ban_status(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        is_banned, ban_reason = await DARKXSIDE78.is_user_banned(user_id)
        if is_banned:
            await message.reply_text(
                f"**Yᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.**\n\n**Rᴇᴀsᴏɴ:** {ban_reason}"
            )
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

@Client.on_message(filters.command("refer") & filters.private)
@check_ban_status
async def refer(client, message):
    user_id = message.from_user.id
    user = await DARKXSIDE78.col.find_one({"_id": user_id})

    if not user or not user.get("referral_code"):
        referral_code = secrets.token_hex(4)
        await DARKXSIDE78.col.update_one(
            {"_id": user_id},
            {"$set": {"referral_code": referral_code}},
            upsert=True
        )
    else:
        referral_code = user["referral_code"]

    referrals = user.get("referrals", []) if user else []
    count = len(referrals)

    refer_link = f"https://t.me/{Config.BOT_USERNAME}?start=ref_{referral_code}"
    await message.reply_text(
        f"**Your Referral Link:**\n{refer_link}\n\n"
        f"**Total Referrals:** {count}\n"
        f"**You get 100 tokens for every successful referral!**"
    )

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
        
        new_tokens = int(amount) + user.get('token', 69)
        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {"token": new_tokens}}
        )
        await message.reply_text(f"🗸 Aᴅᴅᴇᴅ {amount} ᴛᴏᴋᴇɴs ᴛᴏ ᴜsᴇʀ {user['_id']}. Nᴇᴡ ʙᴀʟᴀɴᴄᴇ: {new_tokens}")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /add_token <amount> @username/userid")

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
        await message.reply_text(f"**✘ Rᴇᴍᴏᴠᴇᴅ {amount} ᴛᴏᴋᴇɴs ғʀᴏᴍ ᴜsᴇʀ {user['_id']}. Nᴇᴡ ʙᴀʟᴀɴᴄᴇ: {new_tokens}**")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /remove_token <amount> @username/userid")

@Client.on_message(filters.command("add_premium") & filters.user(Config.ADMIN))
async def add_premium(bot: Client, message: Message):
    try:
        cmd, user_ref, duration = message.text.split(maxsplit=2)
        duration = duration.lower()
        
        if user_ref.startswith("@"):
            user = await DARKXSIDE78.col.find_one({"username": user_ref[1:]})
        else:
            user = await DARKXSIDE78.col.find_one({"_id": int(user_ref)})
        
        if not user:
            return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
        
        if duration == "lifetime":
            expiry = datetime(9999, 12, 31)
        else:
            num, unit = duration[:-1], duration[-1]
            unit_map = {
                'h': 'hours',
                'd': 'days',
                'm': 'months',
                'y': 'years'
            }
            delta = timedelta(**{unit_map[unit]: int(num)})
            expiry = datetime.now() + delta
        
        await DARKXSIDE78.col.update_one(
            {"_id": user['_id']},
            {"$set": {
                "is_premium": True,
                "premium_expiry": expiry
            }}
        )
        await message.reply_text(f"**🗸 Pʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴜɴᴛɪʟ {expiry}**")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /add_premium @username/userid ")

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
        await message.reply_text("**✘ Pʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʀᴇᴍᴏᴠᴇᴅ**")
    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {e}\nUsᴀɢᴇ: /remove_premium @username/userid")

@Client.on_message(filters.private & filters.command(["token", "mytokens", "bal"]))
async def check_tokens(client, message: Message):
    user_id = message.from_user.id
    user_data = await DARKXSIDE78.col.find_one({"_id": user_id})
    
    if not user_data:
        return await message.reply_text("**Eʀʀᴏʀ: DARK**")
    
    is_premium = user_data.get("is_premium", False)
    premium_expiry = user_data.get("premium_expiry")

    if is_premium and premium_expiry:
        if datetime.now() > premium_expiry:
            is_premium = False
            await DARKXSIDE78.col.update_one(
                {"_id": user_id},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )

    token_count = user_data.get("token", Config.DEFAULT_TOKEN)
    msg = [
        "**Yᴏᴜʀ Aᴄᴄᴏᴜɴᴛ Sᴛᴀᴛᴜs**",
        "",
        f"**Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs:** {'🗸 Aᴄᴛɪᴠᴇ' if is_premium else '✘ Iɴᴀᴄᴛɪᴠᴇ'}"
    ]
    
    if is_premium and premium_expiry:
        msg.append(f"**Pʀᴇᴍɪᴜᴍ Exᴘɪʀʏ:** {premium_expiry.strftime('%d %b %Y %H:%M')}")
    else:
        msg.extend([
            f"**Aᴠᴀɪʟᴀʙʟᴇ Tᴏᴋᴇɴs:** {token_count}",
            "",
            "**1 ᴛᴏᴋᴇɴ = 1 ғɪʟᴇ ʀᴇɴᴀᴍᴇ**",
            ""
        ])
    
    buttons = []
    if not is_premium:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Gᴇɴᴇʀᴀᴛᴇ Mᴏʀᴇ Tᴏᴋᴇɴs", callback_data="gen_tokens")],
            [InlineKeyboardButton("Gᴇᴛ Pʀᴇᴍɪᴜᴍ", callback_data="premium_info")]
        ])
    else:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Rᴇғʀᴇsʜ Sᴛᴀᴛᴜs", callback_data="refresh_tokens")]
        ])
    
    await message.reply_text(
        "\n".join(msg),
        reply_markup=buttons,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex(r"^(gen_tokens|premium_info|refresh_tokens)$"))
async def token_buttons_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    user_data = await DARKXSIDE78.col.find_one({"_id": user_id})
    
    if data == "gen_tokens":
        await query.message.edit_text(
            "**Yᴏᴜ ᴄᴀɴ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴏᴋᴇɴs ᴜsɪɴɢ /gentoken** 🔗",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{Config.SUPPORT_CHANNEL_USERNAME}")],
                [InlineKeyboardButton("Bᴀᴄᴋ", callback_data="token_back")]
            ]),
            disable_web_page_preview=True
        )
    
    elif data == "premium_info":
        await query.message.edit_text(
            Txt.PREMIUM_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{Config.SUPPORT_CHANNEL_USERNAME}")],
                [InlineKeyboardButton("Bᴀᴄᴋ", callback_data="token_back")]
            ]),
            disable_web_page_preview=True
        )
    
    elif data == "refresh_tokens":
        await check_tokens(client, query.message)
        await query.answer("Status refreshed!")
    
    elif data == "token_back":
        await check_tokens(client, query.message)


logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("gentoken") & filters.private)
@check_ban_status
async def generate_token(client: Client, message: Message):
    user_id = message.from_user.id
    db = DARKXSIDE78
    
    token_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=Config.TOKEN_ID_LENGTH))
    
    deep_link = f"https://t.me/{Config.BOT_USERNAME}?start={token_id}"
    
    short_url = await shorten_url(deep_link)
    
    if not short_url:
        return await message.reply("**Fᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴏᴋᴇɴ ʟɪɴᴋ. Pʟᴇᴀsᴇ ᴛʀʏ ʟᴀᴛᴇʀ.**")
    
    await db.create_token_link(user_id, token_id, Config.SHORTENER_TOKEN_GEN)
    
    await message.reply(
        f"**Gᴇᴛ 100 Tᴏᴋᴇɴs**\n\n"
        f"**Cʟɪᴄᴋ ʙᴇʟᴏᴡ ʟɪɴᴋ ᴀɴᴅ ᴄᴏᴍᴘʟᴇᴛᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ:**\n{short_url}\n\n"
        "**Lɪɴᴋ ᴠᴀʟɪᴅ ғᴏʀ 24 ʜᴏᴜʀs | Oɴᴇ-ᴛɪᴍᴇ ᴜsᴇ ᴏɴʟʏ**",
        disable_web_page_preview=True
    )

async def handle_token_redemption(client: Client, message: Message, token_id: str):
    user_id = message.from_user.id
    
    try:
        token_data = await DARKXSIDE78.get_token_link(token_id)
        
        if not token_data:
            return await message.reply("**Iɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴛᴏᴋᴇɴ ʟɪɴᴋ...**")
        
        if token_data['used']:
            return await message.reply("**Tʜɪs ʟɪɴᴋ ʜᴀs ᴀʟʀᴇᴀᴅʏ ʙᴇᴇɴ ᴜsᴇᴅ...**")
        
        expiry_utc = token_data['expiry'].replace(tzinfo=pytz.UTC)
        
        if datetime.now(pytz.UTC) > expiry_utc:
            return await message.reply("Tᴏᴋᴇɴ ᴇxᴘɪʀᴇᴅ...")
        
        if token_data['user_id'] != user_id:
            return await message.reply("**Tʜɪs ᴛᴏᴋᴇɴ ʟɪɴᴋ ʙᴇʟᴏɴɢs ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴜsᴇʀ...**")
        
        await DARKXSIDE78.col.update_one(
            {"_id": user_id},
            {"$inc": {"token": token_data['tokens']}}
        )
        
        await DARKXSIDE78.mark_token_used(token_id)
        
        await message.reply(f"Sᴜᴄᴄᴇss! {token_data['tokens']} ᴛᴏᴋᴇɴs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ!")
    
    except Exception as e:
        logging.error(f"Error during token redemption: {e}")
        await message.reply("**Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**")

@Client.on_message(filters.private & filters.command("start"))
@check_ban_status
async def start(client, message: Message):
    user = message.from_user
    user_id = user.id

    if len(message.command) > 1:
        arg = message.command[1]
        if arg.startswith("ref_"):
            referral_code = arg[4:]
            referrer = await DARKXSIDE78.col.find_one({"referral_code": referral_code})
            if referrer and referrer["_id"] != user_id:
                updated = await DARKXSIDE78.col.update_one(
                    {"_id": referrer["_id"]},
                    {"$addToSet": {"referrals": user_id}}
                )
                if updated.modified_count > 0:
                    await DARKXSIDE78.col.update_one(
                        {"_id": referrer["_id"]},
                        {"$inc": {"token": Config.REFER_TOKEN}}
                    )
                    try:
                        await client.send_message(
                            referrer["_id"],
                            f"**You received {Config.REFER_TOKEN} tokens for referring {user.mention}!**"
                        )
                    except Exception:
                        pass
        else:
            await handle_token_redemption(client, message, arg)
            return

    await DARKXSIDE78.add_user(client, message)

    m = await message.reply_text("𝙏𝙝𝙚 𝙈𝙤𝙣𝙖𝙧𝙘𝙝 𝙞𝙨 𝙖𝙬𝙖𝙠𝙚𝙣𝙞𝙣𝙜...")
    await asyncio.sleep(0.6)
    await m.edit_text("🌑 𝙎𝙝𝙖𝙙𝙤𝙬𝙨 𝙖𝙧𝙚 𝙨𝙩𝙞𝙧𝙧𝙞𝙣𝙜...")
    await asyncio.sleep(0.5)
    await m.edit_text("👣 𝙃𝙞𝙨 𝙛𝙤𝙤𝙩𝙨𝙩𝙚𝙥𝙨 𝙚𝙘𝙝𝙤 𝙞𝙣 𝙩𝙝𝙚 𝙙𝙖𝙧𝙠𝙣𝙚𝙨𝙨...")
    await asyncio.sleep(0.5)
    await m.edit_text("⚔️ 𝙎𝙪𝙣𝙜 𝙅𝙞𝙣-𝙒𝙤𝙤 𝙝𝙖𝙨 𝙖𝙧𝙧𝙞𝙫𝙚𝙙.")
    await asyncio.sleep(0.5)
    await m.delete()


    await message.reply_sticker(Config.START_STICKER)

    buttons = InlineKeyboardMarkup([
        [   # A R I S E row at the top
            InlineKeyboardButton(text="ᴀ", callback_data="help"),       # A
            InlineKeyboardButton(text="ʀ", callback_data="help"),  # R
            InlineKeyboardButton(text="ɪ", callback_data="about"),       # I
            InlineKeyboardButton(text="ꜱ", callback_data="premiumx"),        # S
            InlineKeyboardButton(text="ᴇ", callback_data="help")  # E
        ],
        [
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', url= "https://t.me/TFIBOTS"),
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url= "https://t.me/TFIBOTS_SUPPORT")
        ],
        [
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ', callback_data='premiumx')
        ],
        [
            InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs", callback_data='help')
        ]
    ])

    if Config.START_PIC:
        await message.reply_photo(
            Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            text=Txt.START_TXT.format(user.mention),
            reply_markup=buttons,
            disable_web_page_preview=True
        )

async def shorten_url(deep_link: str) -> str:
    api_url = f"{Config.SHORTENER_URL}?api={Config.TOKEN_API}&url={quote(deep_link)}&format=text"
    try:
        async with aiohttp.ClientSession() as session:
            max_retries = 3
            for attempt in range(max_retries):
                async with session.get(api_url, ssl=True) as response:
                    if response.status == 200:
                        return (await response.text()).strip()
                    logging.error(f"API Error: {response.status}")
                await asyncio.sleep(2 ** attempt)
    except Exception as e:
        logging.error(f"Connection Error: {e}")
    logging.warning("Shorten URL API failed. Using original deep link.")
    return deep_link

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    print(f"Callback data received: {data}")

    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', url=f'https://t.me/mymopies'), InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ', url=f'https://t.me/mymopies')],
                [InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('ᴘʀᴇᴍɪᴜᴍ', callback_data='premiumx')],
                [InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs", callback_data='help')]
            ])
        )
    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help")]
            ])
        )

    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
        #    disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ", callback_data='file_names')],
                [InlineKeyboardButton('ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'), InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ', callback_data='caption')],
                [InlineKeyboardButton('ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta'), InlineKeyboardButton('more', callback_data='settings_menu')],
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home')]
            ])
        )

    elif data == "meta":
        await query.message.edit_text(
            text=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help")]
            ])
        )

    elif data == "file_names":
        format_template = await DARKXSIDE78.get_format_template(user_id)
        await query.message.edit_text(
            text=Txt.FILE_NAME_TXT.format(format_template=format_template),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help")]
            ])
        )
    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help")]
            ])
        )
    elif data == "metadatax":
        await query.message.edit_caption(
            caption=Txt.SEND_METADATA,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help")]
            ])
        )
    elif data == "source":
        await query.message.edit_caption(
            caption=Txt.SOURCE_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="home")]
            ])
        )
    elif data == "premiumx":
        await query.message.edit_caption(
            caption=Txt.PREMIUM_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton("ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ", url=f'https://t.me/{Config.OWNER_USERNAME}')]
            ])
        )
    elif data == "plans":
        await query.message.edit_caption(
            caption=Txt.PREPLANS_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close"), InlineKeyboardButton("ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ", url=f'https://t.me/{Config.OWNER_USERNAME}')]
            ])
        )
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{Config.SUPPORT_CHANNEL_USERNAME}'), InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs", callback_data="help")],
                [InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=f'https://t.me/{Config.DEVELOPER_USERNAME}'), InlineKeyboardButton("ɴᴇᴛᴡᴏʀᴋ", url=f'https://t.me/{Config.BOT_CHANNEL_USERNAME}')],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="home")]
            ])
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()

    elif data == "settings_menu":
        await query.message.edit_text(
            text="**WHERE DO YOU WANT TO OPEN THE SETTINGS MENU?**",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                # First row
                [InlineKeyboardButton("ꜱᴏʀᴛ", callback_data="sort"),
                 InlineKeyboardButton("ᴜᴘꜱᴄᴀʟᴇ", callback_data="upscale_settings"),
                 InlineKeyboardButton("ꜰᴏɴᴛ", callback_data="font_settings")],
                
                # Second row
                [InlineKeyboardButton("ᴛᴏᴏʟꜱ", callback_data="tools_settings"),
                 InlineKeyboardButton("ᴛᴏᴋᴇɴꜱ", callback_data="tokens_settings"),
                 InlineKeyboardButton("ᴀɴɪᴍᴇ", callback_data="anime_settings")],
                
                # Third row
                [InlineKeyboardButton("ᴘᴅꜰ ᴛᴏᴏʟꜱ", callback_data="pdf_tools_settings"),
                 InlineKeyboardButton("ᴛᴇʟᴇɢʀᴀᴘʜ", callback_data="tmg_link_settings"),
                 InlineKeyboardButton("ꜱᴛɪᴄᴋᴇʀ", callback_data="sticker_settings")],
                
                # Navigation row
                [InlineKeyboardButton("◁", callback_data="help"),
                 InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="help"),
                 InlineKeyboardButton("▷", callback_data="next_page_settings")]
            ])
        )
    
    # Dummy callbacks for each button
    elif data == "sort":
        await query.message.edit_caption(
            caption=Txt.SORT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )
    elif data == "upscale_settings":
        await query.message.edit_caption(
            caption=Txt.UPSCALE_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )
    elif data == "font_settings":
        await query.message.edit_caption(
            caption=Txt.FONT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )
    elif data == "tools_settings":
        await query.message.edit_caption(
                caption=Txt.TOOLS_TXT,
                reply_markup=InlineKeyboardMarkup([
                   [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
                ])
            )
    elif data == "tokens_settings":
        await query.message.edit_caption(
            caption=Txt.TOKEN_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )    
    elif data == "anime_settings":
        await query.message.edit_caption(
            caption=Txt.ANIME_TXT,
            reply_markup=InlineKeyboardMarkup([
               [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )    
    elif data == "pdf_tools_settings":
        await query.message.edit_caption(
            caption=Txt.PDF_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )    
    elif data == "tmg_link_settings":
        await query.message.edit_caption(
            caption=Txt.TELEGRAPH_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
            ])
        )    
    elif data == "sticker_settings":
        await query.message.edit_caption(
            caption=Txt.STICKER_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="settings_menu")]
           ])   
        ) 
    elif data == "next_page_settings":
        await query.answer("SHARE AND SUPPORT US ", show_alert=False)
    

"""
@Client.on_message(filters.command("donate"))
@check_ban_status
async def donation(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help"), InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f'https://t.me/{Config.OWNER_USERNAME}')]
    ])
    yt = await message.reply_photo(photo='https://graph.org/file/1919fe077848bd0783d4c.jpg', caption=Txt.DONATE_TXT, reply_markup=buttons)
    await asyncio.sleep(300)
    await yt.delete()
    await message.delete()
"""
@Client.on_message(filters.command("premium"))
@check_ban_status
async def getpremium(bot, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴏᴡɴᴇʀ", url=f"https://t.me/{Config.OWNER_USERNAME}"), InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
    ])
    yt = await message.reply_photo(photo='https://graph.org/file/feebef43bbdf76e796b1b.jpg', caption=Txt.PREMIUM_TXT, reply_markup=buttons)
    await asyncio.sleep(300)
    await yt.delete()
    await message.delete()

@Client.on_message(filters.command("plan"))
@check_ban_status
async def premium(bot, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("sᴇɴᴅ ss", url=f"https://t.me/{Config.OWNER_USERNAME}"), InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
    ])
    yt = await message.reply_photo(photo='https://graph.org/file/8b50e21db819f296661b7.jpg', caption=Txt.PREPLANS_TXT, reply_markup=buttons)
    await asyncio.sleep(300)
    await yt.delete()
    await message.delete()

@Client.on_message(filters.command("bought") & filters.private)
@check_ban_status
async def bought(client, message):
    msg = await message.reply('Wᴀɪᴛ ᴄʜᴇᴄᴋɪɴɢ...')
    replied = message.reply_to_message

    if not replied:
        await msg.edit("<b>Please reply with the screenshot of your payment for the premium purchase to proceed.\n\nFor example, first upload your screenshot, then reply to it using the '/bought' command</b>")
    elif replied.photo:
        await client.send_photo(
            chat_id=LOG_CHANNEL,
            photo=replied.photo.file_id,
            caption=f'<b>User - {message.from_user.mention}\nUser id - <code>{message.from_user.id}</code>\nUsername - <code>{message.from_user.username}</code>\nName - <code>{message.from_user.first_name}</code></b>',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Close", callback_data="close_data")]
            ])
        )
        await msg.edit_text('<b>Yᴏᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ Aᴅᴍɪɴs</b>')

@Client.on_message(filters.private & filters.command("help"))
@check_ban_status
async def help_command(client, message):
    bot = await client.get_me()
    mention = bot.mention

    await message.reply_text(
        text=Txt.HELP_TXT.format(mention=mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ", callback_data='file_names')],
            [InlineKeyboardButton('ᴛʜᴜᴍʙɴᴀɪʟ', callback_data='thumbnail'), InlineKeyboardButton('ᴄᴀᴘᴛɪᴏɴ', callback_data='caption')],
            [InlineKeyboardButton('ᴍᴇᴛᴀᴅᴀᴛᴀ', callback_data='meta'), InlineKeyboardButton('ᴍᴏʀᴇ', callback_data='settings_menu')],
            [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home')]
        ])
    )
    
    
# Command to open settings
@Client.on_message(filters.private & filters.command("settings" "panel"))
async def settings_command(client, message):
    await message.reply_text(
        text="**WHERE DO YOU WANT TO OPEN THE SETTINGS MENU?**",
        reply_markup=InlineKeyboardMarkup([
                # First row
                [InlineKeyboardButton("ꜱᴏʀᴛ", callback_data="sort"),
                 InlineKeyboardButton("ᴜᴘꜱᴄᴀʟᴇ", callback_data="upscale_settings"),
                 InlineKeyboardButton("ꜰᴏɴᴛ", callback_data="font_settings")],
                
                # Second row
                [InlineKeyboardButton("ᴛᴏᴏʟꜱ", callback_data="tools_settings"),
                 InlineKeyboardButton("ᴛᴏᴋᴇɴꜱ", callback_data="tokens_settings"),
                 InlineKeyboardButton("ᴀɴɪᴍᴇ", callback_data="anime_settings")],
                
                # Third row
                [InlineKeyboardButton("ᴘᴅꜰ ᴛᴏᴏʟꜱ", callback_data="pdf_tools_settings"),
                 InlineKeyboardButton("ᴛᴇʟᴇɢʀᴀᴘʜ", callback_data="tmg_link_settings"),
                 InlineKeyboardButton("ꜱᴛɪᴄᴋᴇʀ", callback_data="sticker_settings")],
                
                # Navigation row
                [InlineKeyboardButton("◁", callback_data="help"),
                 InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="help"),
                 InlineKeyboardButton("▷", callback_data="next_page_settings")]
        ])
    )



# ⛓ Handler for Groups - Reply to media with command
@Client.on_message(filters.command(["img", "tgm", "telegraph"], prefixes="/") & filters.reply)
async def c_upload(client, message: Message):
    reply = message.reply_to_message
    if not reply.media:
        return await message.reply_text("Reply to a media to upload it to Cloud.")
    if reply.document and reply.document.file_size > 5 * 1024 * 1024:  # 5 MB
        return await message.reply_text("File size limit is 5 MB.")
    msg = await message.reply_text("Processing...")
    try:
        downloaded_media = await reply.download()
        if not downloaded_media:
            return await msg.edit_text("Something went wrong during download.")
        with open(downloaded_media, "rb") as f:
            data = f.read()
            resp = requests.post("https://envs.sh", files={"file": data})
            if resp.status_code == 200:
                await msg.edit_text(f"{resp.text}")
            else:
                await msg.edit_text("Something went wrong. Please try again later.")
        os.remove(downloaded_media)
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")

