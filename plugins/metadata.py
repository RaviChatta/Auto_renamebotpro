from helper.database import DARKXSIDE78 as db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from config import *
from functools import wraps
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_ban_status(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        is_banned, ban_reason = await db.is_user_banned(user_id)
        if is_banned:
            await message.reply_text(
                f"**You are banned from using this bot.**\n\n**Reason:** {ban_reason}"
            )
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

async def generate_metadata_text(user_id: int) -> str:
    """Generate the metadata display text"""
    current = await db.get_metadata(user_id)
    title = await db.get_title(user_id)
    author = await db.get_author(user_id)
    artist = await db.get_artist(user_id)
    video = await db.get_video(user_id)
    audio = await db.get_audio(user_id)
    subtitle = await db.get_subtitle(user_id)
    encoded_by = await db.get_encoded_by(user_id)
    custom_tag = await db.get_custom_tag(user_id)
    commentz = await db.get_commentz(user_id)

    return f"""
**㊋ Your Metadata is currently: {current}**

**◈ Title ▹** `{title if title else 'Not found'}`  
**◈ Author ▹** `{author if author else 'Not found'}`  
**◈ Artist ▹** `{artist if artist else 'Not found'}`  
**◈ Audio ▹** `{audio if audio else 'Not found'}`  
**◈ Subtitle ▹** `{subtitle if subtitle else 'Not found'}`  
**◈ Video ▹** `{video if video else 'Not found'}`  
**◈ Encoded By ▹** `{encoded_by if encoded_by else 'Not found'}`
**◈ Custom Tag ▹** `{custom_tag if custom_tag else 'Not found'}`
**◈ Comment ▹** `{commentz if commentz else 'Not found'}`
    """

async def generate_metadata_buttons(user_id: int) -> InlineKeyboardMarkup:
    """Generate the metadata buttons"""
    current = await db.get_metadata(user_id)
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"On{' ✅' if current == 'On' else ''}", callback_data='on_metadata'),
            InlineKeyboardButton(f"Off{' ✅' if current == 'Off' else ''}", callback_data='off_metadata')
        ],
        [
            InlineKeyboardButton("Metadata Help", callback_data="meta_help"),
            InlineKeyboardButton("Close", callback_data="close_meta")
        ]
    ])

@Client.on_message(filters.command("metadata"))
@check_ban_status
async def metadata_command(client: Client, message: Message):
    """Handle /metadata command"""
    try:
        text = await generate_metadata_text(message.from_user.id)
        buttons = await generate_metadata_buttons(message.from_user.id)
        await message.reply_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in metadata command: {e}")
        await message.reply_text("An error occurred while processing your request.")

@Client.on_callback_query(filters.regex(r"^(on_metadata|off_metadata|meta_help|close_meta)$"))
async def metadata_callback_handler(client: Client, query: CallbackQuery):
    """Handle all metadata-related callbacks"""
    user_id = query.from_user.id
    data = query.data

    try:
        if data == "on_metadata":
            await db.set_metadata(user_id, "On")
            await query.answer("Metadata enabled!")
        elif data == "off_metadata":
            await db.set_metadata(user_id, "Off")
            await query.answer("Metadata disabled!")
        elif data == "meta_help":
            await query.message.edit_text(
                text=Txt.META_TXT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Back", callback_data="meta_back"),
                        InlineKeyboardButton("Close", callback_data="close_meta")
                    ]
                ])
            )
            return
        elif data == "close_meta":
            await query.message.delete()
            return
        elif data == "meta_back":
            pass  # Will fall through to the refresh below

        # Refresh the metadata display
        text = await generate_metadata_text(user_id)
        buttons = await generate_metadata_buttons(user_id)
        await query.message.edit_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )

    except Exception as e:
        logger.error(f"Error in metadata callback: {e}")
        await query.answer("An error occurred. Please try again.", show_alert=True)

# ==================== METADATA SET COMMANDS ====================

async def handle_metadata_setting(command: str, message: Message, field_name: str, example: str):
    """Generic handler for metadata setting commands"""
    if len(message.command) == 1:
        return await message.reply_text(
            f"**Provide the {field_name}\n\nExample: {example}**"
        )
    value = message.text.split(" ", 1)[1]
    try:
        await getattr(db, f"set_{field_name.lower()}")(message.from_user.id, value)
        await message.reply_text(f"**✅ {field_name.capitalize()} Saved**")
    except Exception as e:
        logger.error(f"Error setting {field_name}: {e}")
        await message.reply_text(f"Failed to save {field_name}. Please try again.")

@Client.on_message(filters.private & filters.command('settitle'))
@check_ban_status
async def set_title(client: Client, message: Message):
    await handle_metadata_setting(
        "/settitle", message, "title",
        f"/settitle Encoded By {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setauthor'))
@check_ban_status
async def set_author(client: Client, message: Message):
    await handle_metadata_setting(
        "/setauthor", message, "author",
        f"/setauthor {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setartist'))
@check_ban_status
async def set_artist(client: Client, message: Message):
    await handle_metadata_setting(
        "/setartist", message, "artist",
        f"/setartist {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setaudio'))
@check_ban_status
async def set_audio(client: Client, message: Message):
    await handle_metadata_setting(
        "/setaudio", message, "audio",
        f"/setaudio {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setsubtitle'))
@check_ban_status
async def set_subtitle(client: Client, message: Message):
    await handle_metadata_setting(
        "/setsubtitle", message, "subtitle",
        f"/setsubtitle {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setvideo'))
@check_ban_status
async def set_video(client: Client, message: Message):
    await handle_metadata_setting(
        "/setvideo", message, "video",
        f"/setvideo Encoded by {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setencoded_by'))
@check_ban_status
async def set_encoded_by(client: Client, message: Message):
    await handle_metadata_setting(
        "/setencoded_by", message, "encoded_by",
        f"/setencoded_by {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setcustom_tag'))
@check_ban_status
async def set_custom_tag(client: Client, message: Message):
    await handle_metadata_setting(
        "/setcustom_tag", message, "custom_tag",
        f"/setcustom_tag {Config.SHOW_CHANNEL}"
    )

@Client.on_message(filters.private & filters.command('setcomment'))
@check_ban_status
async def set_comment(client: Client, message: Message):
    await handle_metadata_setting(
        "/setcomment", message, "commentz",
        f"/setcomment {Config.SHOW_CHANNEL}"
    )
