from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import DARKXSIDE78
from pyrogram.types import CallbackQuery
import pytz
import logging
from math import ceil
from functools import wraps
from config import Config
from datetime import datetime

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message((filters.private | filters.group) & filters.command("rename_history"))
@check_ban_status
async def rename_history(client, message):
    args = message.text.split(maxsplit=1)
    user_id = message.from_user.id

    is_admin = user_id in Config.ADMINS
    is_premium = await DARKXSIDE78.is_premium(user_id)

    if len(args) > 1 and (is_admin or is_premium):
        try:
            target_user_id = int(args[1])
        except ValueError:
            return await message.reply_text("**Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀ ID.**")
    else:
        target_user_id = user_id

    history = await DARKXSIDE78.get_rename_history(target_user_id)
    if not history:
        return await message.reply_text("**Nᴏ ʀᴇɴᴀᴍᴇ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ.**")

    items_per_page = 15
    total_pages = ceil(len(history) / items_per_page)
    current_page = 1

    sent = await message.reply_text("**Lᴏᴀᴅɪɴɢ ʜɪsᴛᴏʀʏ...**", quote=True)
    await send_history_page(client, sent, history, current_page, total_pages, items_per_page, target_user_id, edit=True)


async def send_history_page(client, message, history, current_page, total_pages, items_per_page, target_user_id, edit=False):
    """Send or edit a specific page of rename history with navigation buttons."""
    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    page_items = history[start_index:end_index]

    history_text = "\n".join([
        f"**Oʀɪɢɪɴᴀʟ:** `{item.get('original_name', 'Unknown')}` ➨ **Rᴇɴᴀᴍᴇᴅ:** `{item.get('renamed_name', 'Unknown')}`"
        for item in page_items
    ])
    text = (
        f"**Rᴇɴᴀᴍᴇ Hɪsᴛᴏʀʏ ғᴏʀ Usᴇʀ {target_user_id} (Pᴀɢᴇ {current_page}/{total_pages}):**\n\n"
        f"{history_text}"
    )

    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton("« Pʀᴇᴠɪᴏᴜs", callback_data=f"history_page_{current_page - 1}_{target_user_id}"))
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Nᴇxᴛ »", callback_data=f"history_page_{current_page + 1}_{target_user_id}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

    await message.edit_text(text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex(r"^history_page_\d+_\d+$"))
async def handle_history_pagination(client, callback_query: CallbackQuery):
    """Handle pagination for rename history."""
    data = callback_query.data.split("_")
    current_page = int(data[2])
    target_user_id = int(data[3])

    history = await DARKXSIDE78.get_rename_history(target_user_id)
    if not history:
        return await callback_query.answer("Nᴏ ʀᴇɴᴀᴍᴇ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ.", show_alert=True)

    items_per_page = 15
    total_pages = ceil(len(history) / items_per_page)


    await send_history_page(client, callback_query.message, history, current_page, total_pages, items_per_page, target_user_id, edit=True)
    await callback_query.answer()

@Client.on_message(filters.private & filters.command("autorename"))
@check_ban_status
async def auto_rename_command(client, message):
    try:
        user_id = message.from_user.id

        # Extract template from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2 or not command_parts[1].strip():
            await message.reply_text(
                "<b>⚠️ Please provide a rename template.</b>\n\n"
                "<b>🧾 Format:</b>\n"
                "<code>/autorename [S{season}E{episode}] {title} [{resolution}] [{audio}]</code>\n\n"
                "<b>🎬 Input:</b>\n"
                "<code>World Trigger S01E03 [1080p] [Dual].mkv</code>\n"
                "<b>📁 Output:</b>\n"
                "<code>[S01E03] World Trigger [1080p] [Dual].mkv</code>\n\n"
                "<b>🎬 Input (Movie):</b>\n"
                "<code>Firefly (2025) HQ HDRip - x264 - [Tam + Tel + Hin + Mal] - (AAC 2.0) - 850MB - ESub.mkv</code>\n"
                "<b>📁 Output:</b>\n"
                "<code>Firefly (2025) [HDRip] [Tam + Tel + Hin + Mal] [x264].mkv</code>\n\n"
                "<b>📌 Notes:</b>\n"
                • The bot will use this template to rename your files automatically.\n"
                • Enable with <code>/autorename_on</code> • Disable with <code>/autorename_off</code>\n"
                • <code>{title}</code> extracts the main title, removing season/episode/quality/metadata."
            )

            return

        # Save template for user or process further
        format_template = command_parts[1].strip()

        await DARKXSIDE78.set_format_template(user_id, format_template)
        
        await message.reply_text(
                "**Aᴜᴛᴏ-ʀᴇɴᴀᴍᴇ ᴛᴇᴍᴘʟᴀᴛᴇ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
                f"**Yᴏᴜʀ ᴛᴇᴍᴘʟᴀᴛᴇ:** `{format_template}`\n\n"
                "**Nᴏᴡ ᴡʜᴇɴ ʏᴏᴜ sᴇɴᴅ ғɪʟᴇs, ᴛʜᴇʏ'ʟʟ ʙᴇ ʀᴇɴᴀᴍᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴜsɪɴɢ ᴛʜɪs ғᴏʀᴍᴀᴛ.**"
        )
    except Exception as e:
        logger.error(f"Error in auto_rename_command: {e}", exc_info=True)
        await message.reply_text("**Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴇᴛᴛɪɴɢ ᴛʜᴇ ᴀᴜᴛᴏ-ʀᴇɴᴀᴍᴇ ᴛᴇᴍᴘʟᴀᴛᴇ.**")

@Client.on_message(filters.private & filters.command("setmedia"))
@check_ban_status
async def set_media_command(client, message):
    """Initiate media type selection with a sleek inline keyboard."""
    keyboard = InlineKeyboardMarkup([
        [
                InlineKeyboardButton("Dᴏᴄᴜᴍᴇɴᴛ", callback_data="setmedia_document"),
                InlineKeyboardButton("Vɪᴅᴇᴏ", callback_data="setmedia_video"),
        ],
        [
                InlineKeyboardButton("Aᴜᴅɪᴏ", callback_data="setmedia_audio"),
        ]
    ])

    await message.reply_text(
            "**Sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ:**\n"
            "**Tʜɪs ᴡɪʟʟ ᴅᴇᴛᴇʀᴍɪɴᴇ ʜᴏᴡ ʏᴏᴜʀ ғɪʟᴇs ᴀʀᴇ ʜᴀɴᴅʟᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ.**",
            reply_markup=keyboard,
            quote=True
    )

@Client.on_callback_query(filters.regex(r"^setmedia_"))
async def handle_media_selection(client, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        media_type = callback_query.data.split("_", 1)[1].capitalize()

        try:
            await DARKXSIDE78.set_media_preference(user_id, media_type.lower())
        
            await callback_query.answer(f"Mᴇᴅɪᴀ ᴘʀᴇғᴇʀᴇɴᴄᴇ sᴇᴛ ᴛᴏ {media_type.capitalize()}")
            await callback_query.message.edit_text(
                f"**Mᴇᴅɪᴀ ᴘʀᴇғᴇʀᴇɴᴄᴇ ᴜᴘᴅᴀᴛᴇᴅ!**\n"
                f"**Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ɴᴏᴡ ʙᴇ ʜᴀɴᴅʟᴇᴅ ᴀs {media_type.capitalize()} ᴛʏᴘᴇ.**"
            )
        except Exception as e:
            logger.error(f"Error in handle_media_selection: {e}", exc_info=True)
            await callback_query.answer("Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!")
            await callback_query.message.edit_text(
            "**Eʀʀᴏʀ Sᴇᴛᴛɪɴɢ Pʀᴇғᴇʀᴇɴᴄᴇ**\n"
            "**Cᴏᴜʟᴅɴ'ᴛ sᴇᴛ ᴍᴇᴅɪᴀ ᴘʀᴇғᴇʀᴇɴᴄᴇ ʀɪɢʜᴛ ɴᴏᴡ. Tʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!**"
            )
    except Exception as e:
        logger.error(f"Error in handle_media_selection outer block: {e}", exc_info=True)
        await callback_query.answer("Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!")

@Client.on_message(filters.command(['set_rename_source', 'set_rename', 'set_source', 'setsource']) & filters.private)
@check_ban_status
async def set_rename_source(client, message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Fɪʟᴇɴᴀᴍᴇ", callback_data="setsource_filename"),
            InlineKeyboardButton("Cᴀᴘᴛɪᴏɴ", callback_data="setsource_caption"),
        ]
    ])
    await message.reply_text(
        "**Cʜᴏᴏsᴇ ʏᴏᴜʀ ʀᴇɴᴀᴍᴇ sᴏᴜʀᴄᴇ:**\n"
        "• `Filename`: Usᴇ ᴛʜᴇ ғɪʟᴇ ɴᴀᴍᴇ ғᴏʀ ʀᴇɴᴀᴍɪɴɢ.\n"
        "• `Caption`: Usᴇ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴄᴀᴘᴛɪᴏɴ ғᴏʀ ʀᴇɴᴀᴍɪɴɢ.",
        reply_markup=keyboard,
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^setsource_"))
async def handle_rename_source_selection(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    source = callback_query.data.split("_", 1)[1].lower()
    await DARKXSIDE78.set_metadata_source(user_id, source)
    await callback_query.answer(f"Rᴇɴᴀᴍᴇ sᴏᴜʀᴄᴇ sᴇᴛ ᴛᴏ {source.capitalize()}")
    await callback_query.message.edit_text(
        f"**Rᴇɴᴀᴍᴇ sᴏᴜʀᴄᴇ sᴇᴛ ᴛᴏ:** `{source}`\n"
        f"Nᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴜsᴇ ᴛʜᴇ {source} ғᴏʀ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴠᴀʀɪᴀʙʟᴇs ᴡʜᴇɴ ʀᴇɴᴀᴍɪɴɢ."
    )
@Client.on_message(filters.command(["autorename_on"]) & filters.private)
@check_ban_status
async def autorename_on(client, message):
    user_id = message.from_user.id
    await DARKXSIDE78.set_autorename_status(user_id, True)
    await message.reply_text("✅ **Auto-Rename Mode has been enabled!**\nAll your uploads will be renamed automatically.")

@Client.on_message(filters.command(["autorename_off"]) & filters.private)
@check_ban_status
async def autorename_off(client, message):
    user_id = message.from_user.id
    await DARKXSIDE78.set_autorename_status(user_id, False)
    await message.reply_text("❌ **Auto-Rename Mode has been disabled!**\nYour files will no longer be renamed automatically.")
@Client.on_message(filters.command("autorename_status") & filters.private)
@check_ban_status
async def autorename_status(client, message):
    user_id = message.from_user.id
    status = await DARKXSIDE78.get_autorename_status(user_id)
    text = "🟢 Auto-Rename is currently: <b>ON</b>" if status else "🔴 Auto-Rename is currently: <b>OFF</b>"
    await message.reply_text(text)
