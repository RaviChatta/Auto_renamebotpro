import os
import re
import time
import shutil
import asyncio
import logging
from datetime import datetime, timedelta
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InputMediaDocument, Message
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.enums import ParseMode
from plugins.antinsfw import check_anti_nsfw
from helper.utils import progress_for_pyrogram, humanbytes
from helper.utils import convert
from helper.database import DARKXSIDE78
from config import Config
import random
import string
import aiohttp
import pytz
from asyncio import Semaphore
import subprocess
import json
import aiofiles
import aiofiles.os
import asyncio
from typing import Dict, List, Optional, Set
from collections import deque
from pyrogram import Client, filters
import html
from collections import deque
from typing import Deque, Tuple
from functools import wraps
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import RectangleObject
from PIL import Image
from pyrogram.types import Message
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
import os
import tempfile
from playwright.async_api import async_playwright

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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

renaming_operations = {}
active_sequences = {}
message_ids = {}
flood_control = {}
file_queues = {}
USER_SEMAPHORES = {}
USER_LIMITS = {}
tasks = []
pending_pdf_replace = {}
pending_pdf_insert = {}
global PREMIUM_MODE, PREMIUM_MODE_EXPIRY, ADMIN_MODE
PREMIUM_MODE = Config.GLOBAL_TOKEN_MODE
PREMIUM_MODE_EXPIRY = Config.GLOBAL_TOKEN_MODE
CON_LIMIT_ADMIN = Config.ADMIN_OR_PREMIUM_TASK_LIMIT
CON_LIMIT_NORMAL = Config.NORMAL_TASK_LIMIT
ADMIN_MODE = Config.ADMIN_USAGE_MODE
ADMINS = set(Config.ADMIN)

def parse_duration(arg):
    arg = arg.lower().strip()
    if arg.endswith("d") or arg.endswith("day"):
        return int(re.match(r"(\d+)", arg).group(1))
    elif arg.endswith("m") or arg.endswith("month"):
        num = int(re.match(r"(\d+)", arg).group(1))
        return num * 30
    elif arg.endswith("y") or arg.endswith("year"):
        num = int(re.match(r"(\d+)", arg).group(1))
        return num * 365
    elif arg.isdigit():
        return int(arg)
    return None

@Client.on_message(filters.command("pdf_replace") & filters.reply)
@check_ban_status
async def pdf_replace_banner(client, message: Message):
    replied = message.reply_to_message
    user_id = message.from_user.id
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".pdf"):
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ PDF ᴡɪᴛʜ `/pdf_replace first`, `/pdf_replace last`, ᴏʀ `/pdf_replace first,last`**")
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        return await message.reply("**Sᴘᴇᴄɪꜰʏ ᴡʜɪᴄʜ ᴘᴀɢᴇ⁽s⁾ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ﹕ `/pdf_replace first`, `/pdf_replace last`, ᴏʀ `/pdf_replace first,last`**")
    page_args = [x.strip().lower() for x in args[1].split(",") if x.strip() in ("first", "last")]
    if not page_args:
        return await message.reply("**Oɴʟʏ `first`, `last`, ᴏʀ ʙᴏᴛʜ ᴀʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
    banner_file_id = await DARKXSIDE78.get_pdf_banner(user_id)
    if not banner_file_id:
        return await message.reply("**Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴇᴛ ᴀ PDF ʙᴀɴɴᴇʀ. Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ `/set_pdf_banner` ꜰɪʀsᴛ.**")
    processing_msg = await message.reply("**Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛs...**")
    input_path = await replied.download()
    output_path = input_path
    temp_banner_path = input_path + "_banner.jpg"
    try:
        await client.download_media(banner_file_id, file_name=temp_banner_path)
        reader = PdfReader(input_path)
        writer = PdfWriter()
        num_pages = len(reader.pages)
        img = Image.open(temp_banner_path).convert("RGB")
        img = img.resize((800, 1131))
        img_pdf_path = temp_banner_path + ".pdf"
        img_reader = PdfReader(img_pdf_path)
        img_page = img_reader.pages[0]
        indices = set()
        if "first" in page_args:
            indices.add(0)
        if "last" in page_args:
            indices.add(num_pages - 1)
        for i, page in enumerate(reader.pages):
            if i in indices:
                writer.add_page(img_page)
            else:
                writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        thumb = await DARKXSIDE78.get_thumbnail(message.chat.id)
        thumb_path = None
        if thumb:
            thumb_path = await client.download_media(thumb)
        await client.send_document(
            message.chat.id,
            output_path,
            caption=f"**Rᴇᴘʟᴀᴄᴇᴅ ᴘᴀɢᴇs﹕ {', '.join(page_args)} ᴡɪᴛʜ ʏᴏᴜʀ ʙᴀɴɴᴇʀ.**",
            thumb=thumb_path if thumb_path else None
        )
        if thumb_path:
            os.remove(thumb_path)
        await processing_msg.delete()
    except Exception as e:
        await processing_msg.delete()
        await message.reply(f"**Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴘᴀɢᴇs﹕** `{e}`")
    finally:
        for path in [input_path, output_path, temp_banner_path, temp_banner_path + ".pdf"]:
            if os.path.exists(path):
                os.remove(path)

@Client.on_message(filters.command("pdf_extractor") & filters.reply)
@check_ban_status
async def pdf_extractor_first_last(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".pdf"):
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ PDF ꜰɪʟᴇ ᴡɪᴛʜ `/pdf_extractor`**")
    processing_msg = await message.reply("**Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛs...**")
    input_path = await replied.download()
    first_img_path = None
    last_img_path = None
    try:
        reader = PdfReader(input_path)
        num_pages = len(reader.pages)
        first_img = convert_from_path(input_path, first_page=1, last_page=1)[0]
        last_img = convert_from_path(input_path, first_page=num_pages, last_page=num_pages)[0]
        first_img_path = input_path.replace(".pdf", "_first.jpg")
        last_img_path = input_path.replace(".pdf", "_last.jpg")
        first_img.save(first_img_path, "JPEG")
        last_img.save(last_img_path, "JPEG")
        await client.send_photo(message.chat.id, first_img_path, caption="**Fɪʀsᴛ ᴘᴀɢᴇ ᴀs ɪᴍᴀɢᴇ**")
        await client.send_photo(message.chat.id, last_img_path, caption="**Lᴀsᴛ ᴘᴀɢᴇ ᴀs ɪᴍᴀɢᴇ**")
        await processing_msg.delete()
    except Exception as e:
        await processing_msg.delete()
        await message.reply(f"**Fᴀɪʟᴇᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ᴘᴀɢᴇs﹕** `{e}`")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if first_img_path and os.path.exists(first_img_path):
            os.remove(first_img_path)
        if last_img_path and os.path.exists(last_img_path):
            os.remove(last_img_path)

@Client.on_message(filters.command("pdf_add") & filters.reply)
@check_ban_status
async def pdf_add_banner(client, message: Message):
    replied = message.reply_to_message
    user_id = message.from_user.id
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".pdf"):
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ PDF ᴡɪᴛʜ `/pdf_add first`, `/pdf_add last`, ᴏʀ `/pdf_add first,last`**")
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        return await message.reply("**Sᴘᴇᴄɪꜰʏ ᴡʜᴇʀᴇ ᴛᴏ ᴀᴅᴅ﹕ `/pdf_add first`, `/pdf_add last`, ᴏʀ `/pdf_add first,last`**")
    page_args = [x.strip().lower() for x in args[1].split(",") if x.strip() in ("first", "last")]
    if not page_args:
        return await message.reply("**Oɴʟʏ `first`, `last`, ᴏʀ ʙᴏᴛʜ ᴀʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
    banner_file_id = await DARKXSIDE78.get_pdf_banner(user_id)
    if not banner_file_id:
        return await message.reply("**Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ sᴇᴛ ᴀ PDF ʙᴀɴɴᴇʀ. Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ `/set_pdf_banner` ꜰɪʀsᴛ.**")
    processing_msg = await message.reply("**Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛs...**")
    input_path = await replied.download()
    output_path = input_path
    temp_banner_path = input_path + "_banner.jpg"
    try:
        await client.download_media(banner_file_id, file_name=temp_banner_path)
        reader = PdfReader(input_path)
        writer = PdfWriter()
        num_pages = len(reader.pages)
        img = Image.open(temp_banner_path).convert("RGB")
        img_pdf_path = temp_banner_path + ".pdf"
        img.save(img_pdf_path, "PDF")
        img_reader = PdfReader(img_pdf_path)
        img_page = img_reader.pages[0]
        if "first" in page_args:
            writer.add_page(img_page)
        for page in reader.pages:
            writer.add_page(page)
        if "last" in page_args:
            writer.add_page(img_page)
        with open(output_path, "wb") as f:
            writer.write(f)
        thumb = await DARKXSIDE78.get_thumbnail(message.chat.id)
        thumb_path = None
        if thumb:
            thumb_path = await client.download_media(thumb)
        await client.send_document(
            message.chat.id,
            output_path,
            caption=f"**Aᴅᴅᴇᴅ ʙᴀɴɴᴇʀ ᴘᴀɢᴇ(s): {', '.join(page_args)}**",
            thumb=thumb_path if thumb_path else None
        )
        if thumb_path:
            os.remove(thumb_path)
        await processing_msg.delete()
    except Exception as e:
        await processing_msg.delete()
        await message.reply(f"**Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ ʙᴀɴɴᴇʀ ᴘᴀɢᴇ⁽s⁾﹕** `{e}`")
    finally:
        for path in [input_path, output_path, temp_banner_path, temp_banner_path + ".pdf"]:
            if os.path.exists(path):
                os.remove(path)

@Client.on_message(filters.command("set_pdf_lock"))
@check_ban_status
async def set_pdf_lock_cmd(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        return await message.reply("** Usᴀɢᴇ﹕** `/set_pdf_lock yourpassword`")
    password = args[1].strip()
    await DARKXSIDE78.set_pdf_lock_password(message.from_user.id, password)
    await message.reply("**Dᴇꜰᴀᴜʟᴛ PDF ʟᴏᴄᴋ ᴘᴀssᴡᴏʀᴅ sᴇᴛ﹗ Nᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ `/pdf_lock` ᴡɪᴛʜᴏᴜᴛ sᴘᴇᴄɪꜰʏɪɴɢ ᴀ ᴘᴀssᴡᴏʀᴅ.**")

@Client.on_message(filters.command("pdf_lock") & filters.reply)
@check_ban_status
async def pdf_lock_password(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".pdf"):
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ PDF ꜰɪʟᴇ ᴡɪᴛʜ `/pdf_lock yourpassword`**")
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        password = await DARKXSIDE78.get_pdf_lock_password(message.from_user.id)
        if not password:
            return await message.reply("**Nᴏ ᴘᴀssᴡᴏʀᴅ sᴇᴛ﹗ Usᴇ `/set_pdf_lock yourpassword` ꜰɪʀsᴛ ᴏʀ `/pdf_lock yourpassword`**")
    else:
        password = args[1].strip()
    input_path = await replied.download()
    output_path = input_path.replace(".pdf", "_locked.pdf")
    processing_msg = await message.reply("**Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛs...**")
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        with open(output_path, "wb") as f:
            writer.write(f)
        thumb = await DARKXSIDE78.get_thumbnail(message.chat.id)
        thumb_path = None
        if thumb:
            thumb_path = await client.download_media(thumb)
        await client.send_document(
            message.chat.id,
            output_path,
            caption="**Tʜᴇ PDF ʜᴀs ʙᴇᴇɴ ʟᴏᴄᴋᴇᴅ ᴡɪᴛʜ ʏᴏᴜʀ ᴘᴀssᴡᴏʀᴅ.**",
            thumb=thumb_path if thumb_path else None
        )
        if thumb_path:
            os.remove(thumb_path)
        await processing_msg.delete()
    except Exception as e:
        await processing_msg.delete()
        await message.reply(f"**Fᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴄᴋ PDF﹕** `{e}`")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

@Client.on_message(filters.command("pdf_remove") & filters.reply)
@check_ban_status
async def pdf_remove_pages(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.document or not replied.document.file_name.lower().endswith(".pdf"):
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ PDF ғɪʟᴇ ᴡɪᴛʜ /pdf_remove 1,2,3**")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("**Sᴘᴇᴄɪғʏ ᴘᴀɢᴇs ᴛᴏ ʀᴇᴍᴏᴠᴇ, ᴇ.ɢ. /pdf_remove 1,3,5**")
    remove_pages = [int(x.strip())-1 for x in args[1].split(",") if x.strip().isdigit()]
    input_path = await replied.download()
    output_path = input_path.replace(".pdf", "_removed.pdf")
    processing_msg = await message.reply("**Pʀᴏᴄᴇssɪɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ ᴍᴏᴍᴇɴᴛs...**")
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i not in remove_pages:
                writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        # Fetch user thumbnail if set
        thumb = await DARKXSIDE78.get_thumbnail(message.chat.id)
        thumb_path = None
        if thumb:
            thumb_path = await client.download_media(thumb)
        await client.send_document(
            message.chat.id,
            output_path,
            caption=f"**Rᴇᴍᴏᴠᴇᴅ ᴘᴀɢᴇs: {args[1]}**",
            thumb=thumb_path if thumb_path else None
        )
        if thumb_path:
            os.remove(thumb_path)
        await processing_msg.delete()
    except Exception as e:
        await processing_msg.delete()
        await message.reply(f"**Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘᴀɢᴇs﹕** `{e}`")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

@Client.on_message(filters.command("upscale_ffmpeg") & filters.reply)
@check_ban_status
async def ffmpeg_upscale_photo(client, message):
    replied = message.reply_to_message
    if not replied or not replied.photo:
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ /upscale_ffmpeg ᴛᴏ ᴜᴘsᴄᴀʟᴇ ɪᴛ (ʟᴏᴄᴀʟʟʏ, ɴᴏ API ɴᴇᴇᴅᴇᴅ)﹗**")
    status = await message.reply("**Uᴘsᴄᴀʟɪɴɢ ɪᴍᴀɢᴇ ᴡɪᴛʜ FFᴍᴘᴇɢ... Pʟᴇᴀsᴇ ᴡᴀɪᴛ.**")
    input_path = await replied.download()
    output_path = "upscale_img.jpg"

    try:
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            await status.edit("**Uᴘsᴄᴀʟɪɴɢ ꜰᴀɪʟᴇᴅ﹕ FFᴍᴘᴇɢ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏɴ sᴇʀᴠᴇʀ.**")
            return

        # Get original dimensions
        process = await asyncio.create_subprocess_exec(
            ffmpeg, "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=s=x:p=0", "-i", input_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        width, height = 0, 0
        try:
            dims = stdout.decode().strip().split("x")
            width, height = int(dims[0]), int(dims[1])
        except Exception:
            pass

        target_width = width * 2 if width else 0
        target_height = height * 2 if height else 0

        vf = (
            f"scale={target_width}:{target_height}:flags=lanczos,"
            "hqdn3d=3.0:3.0:8:8,"
            "smartblur=lr=1.0:ls=-1.0:lt=0.8,"
            "unsharp=7:7:1.0:7:7:0.0,"
            "deband"
        )

        cmd = [
            ffmpeg,
            "-y",
            "-i", input_path,
            "-vf", vf,
            output_path
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        if process.returncode != 0 or not os.path.exists(output_path):
            await status.edit(f"**Uᴘsᴄᴀʟɪɴɢ ꜰᴀɪʟᴇᴅ﹕** {stderr.decode().strip()}")
            return

        await client.send_photo(message.chat.id, output_path, caption="**Uᴘsᴄᴀʟᴇᴅ ɪᴍᴀɢᴇ ⁽FFmpeg AI-Like 2x, Sᴍᴏᴏᴛʜ & Dᴇɴᴏɪsᴇᴅ⁾**")
        await status.delete()
    except Exception as e:
        await status.edit(f"**Uᴘsᴄᴀʟɪɴɢ ꜰᴀɪʟᴇᴅ﹕** `{e}`")
    finally:
        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                os.remove(path)
                
@Client.on_message(filters.command("admin_mode"))
async def admin_mode(client, message):
    global ADMIN_MODE
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return await message.reply("Aᴅᴍɪɴ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!")
    
    args = message.text.split()
    if len(args) < 2:
        mode = "on" if ADMIN_MODE else "off"
        return await message.reply(f"Aᴅᴍɪɴ Mᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {mode}")
    
    if args[1].lower() in ("on", "yes", "true"):
        ADMIN_MODE = True
        await message.reply("Aᴅᴍɪɴ Mᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ - Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ")
    else:
        ADMIN_MODE = False
        await message.reply("Aᴅᴍɪɴ Mᴏᴅᴇ ᴅɪsᴀʙʟᴇᴅ - Aʟʟ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss")

@Client.on_message(filters.command("add_admin"))
async def add_admin(client, message):
    if message.from_user.id not in ADMINS:
        return
    
    try:
        target = message.text.split()[1]
        if target.startswith("@"):
            user = await client.get_users(target)
            ADMINS.add(user.id)
        else:
            ADMINS.add(int(target))
        await message.reply(f"Aᴅᴅᴇᴅ ᴀᴅᴍɪɴ: {target}")
    except Exception as e:
        await message.reply(f"Eʀʀᴏʀ: {str(e)}")

class TaskQueue:
    def __init__(self):
        self.queues: Dict[int, Deque[Tuple[str, Message, asyncio.coroutine]]] = {}
        self.processing: Dict[int, Set[str]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.max_retries = 3
        self.locks: Dict[int, asyncio.Lock] = {}
        self.active_processors: Set[int] = set()

    async def add_task(self, user_id: int, file_id: str, message: Message, coro):
        if ADMIN_MODE and user_id not in ADMINS:
            await message.reply_text("Aᴅᴍɪɴ ᴍᴏᴅᴇ ᴀᴄᴛɪᴠᴇ - Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ǫᴜᴇᴜᴇ ғɪʟᴇs!")
            return

        async with self.locks.setdefault(user_id, asyncio.Lock()):
            if user_id not in self.queues:
                self.queues[user_id] = deque()
                self.processing[user_id] = set()

            self.queues[user_id].append((file_id, message, coro))

        if user_id not in USER_SEMAPHORES:
            concurrency_limit = CON_LIMIT_ADMIN if user_id in Config.ADMIN else CON_LIMIT_NORMAL
            USER_SEMAPHORES[user_id] = asyncio.Semaphore(concurrency_limit)
            USER_LIMITS[user_id] = concurrency_limit

        if user_id not in self.active_processors:
            self.active_processors.add(user_id)
            for _ in range(USER_LIMITS[user_id]):
                asyncio.create_task(self._process_user_queue(user_id))

    async def _process_user_queue(self, user_id: int):
        try:
            while True:
                async with self.locks[user_id]:
                    if not self.queues.get(user_id):
                        break
                    file_id, message, coro = self.queues[user_id].popleft()
                    self.processing[user_id].add(file_id)

                semaphore = USER_SEMAPHORES.get(user_id)
                if not semaphore:
                    continue

                async with semaphore:
                    task_id = f"{user_id}:{file_id}"
                    try:
                        for attempt in range(self.max_retries):
                            try:
                                task = asyncio.create_task(coro)
                                self.tasks[task_id] = task
                                await task
                                break
                            except FloodWait as e:
                                await asyncio.sleep(e.value + 1)
                                logger.warning(f"FloodWait for {user_id}: Retry {attempt+1}/{self.max_retries}")
                            except Exception as e:
                                logger.error(f"Task error (attempt {attempt+1}): {e}")
                                if attempt == self.max_retries - 1:
                                    await self._handle_failure(message, file_id, e)
                    finally:
                        async with self.locks[user_id]:
                            self.processing[user_id].discard(file_id)
                            self.tasks.pop(task_id, None)
        finally:
            self.active_processors.discard(user_id)

    async def _handle_failure(self, message: Message, file_id: str, error: Exception):
        try:
            await message.reply_text(
                f"➠ Fᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ғɪʟᴇ ᴀғᴛᴇʀ {self.max_retries} ᴀᴛᴛᴇᴍᴘᴛs\n"
                f"➠ Fɪʟᴇ ID: {file_id}\n"
                f"➠ Eʀʀᴏʀ: {str(error)}"
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def get_queue_status(self, user_id: int) -> dict:
        async with self.locks.get(user_id, asyncio.Lock()):
            return {
                "queued": len(self.queues.get(user_id, [])),
                "processing": len(self.processing.get(user_id, set())),
                "total": len(self.queues.get(user_id, [])) + len(self.processing.get(user_id, set()))
            }

    async def cancel_all(self, user_id: int) -> int:
        async with self.locks.get(user_id, asyncio.Lock()):
            canceled = len(self.queues.get(user_id, []))
            
            if user_id in self.queues:
                self.queues[user_id].clear()
            
            for file_id in list(self.processing.get(user_id, set())):
                task_id = f"{user_id}:{file_id}"
                task = self.tasks.get(task_id)
                if task and not task.done():
                    task.cancel()
                    self.processing[user_id].discard(file_id)
                    self.tasks.pop(task_id, None)
            
            return canceled

task_queue = TaskQueue()

@Client.on_message((filters.group | filters.private) & filters.command("queue"))
@check_ban_status
async def queue_status(client, message: Message):
    user_id = message.from_user.id
    status = await task_queue.get_queue_status(user_id)
    
    await message.reply_text(
        f"**Fɪʟᴇ Qᴜᴇᴜᴇ Sᴛᴀᴛᴜs:**\n"
        f"**➠ Pʀᴏᴄᴇssɪɴɢ: {status['processing']} ғɪʟᴇs**\n"
        f"**➠ Wᴀɪᴛɪɴɢ: {status['queued']} ғɪʟᴇs**\n"
        f"**➠ Tᴏᴛᴀʟ: {status['total']} ғɪʟᴇs**\n\n"
        f"**Usᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴀʟʟ ǫᴜᴇᴜᴇᴅ ᴛᴀsᴋs**"
    )

@Client.on_message((filters.group | filters.private) & filters.command("cancel"))
@check_ban_status
async def cancel_queue(client, message: Message):
    user_id = message.from_user.id
    canceled = await task_queue.cancel_all(user_id)
    
    if canceled > 0:
        await message.reply_text(f"**Cᴀɴᴄᴇʟᴇᴅ {canceled} ǫᴜᴇᴜᴇᴅ ᴛᴀsᴋs!**")
    else:
        await message.reply_text("**Nᴏ ᴛᴀsᴋs ɪɴ ǫᴜᴇᴜᴇ ᴛᴏ ᴄᴀɴᴄᴇʟ.**")

def detect_quality(file_name):
    quality_order = {
        "144p": 1,
        "240p": 2,
        "360p": 3,
        "480p": 4,
        "720p": 5, 
        "1080p": 6,
        "1440p": 7,
        "2160p": 8
        }
    match = re.search(r"(144p|240p|360p|480p|720p|1080p|1440p|2160p)", file_name)
    return quality_order.get(match.group(1), 8) if match else 9

@Client.on_message(filters.command("ssequence") & filters.private)
@check_ban_status
async def start_sequence(client, message: Message):
    user_id = message.from_user.id
    if ADMIN_MODE and user_id not in ADMINS:
        return await message.reply_text("**Aᴅᴍɪɴ ᴍᴏᴅᴇ ɪs ᴀᴄᴛɪᴠᴇ - Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ sᴇǫᴜᴇɴᴄᴇs!**")
        
    if user_id in active_sequences:
        await message.reply_text("**A sᴇǫᴜᴇɴᴄᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ! Usᴇ /esequence ᴛᴏ ᴇɴᴅ ɪᴛ.**")
    else:
        active_sequences[user_id] = []
        message_ids[user_id] = []
        msg = await message.reply_text("**Sᴇǫᴜᴇɴᴄᴇ ʜᴀs ʙᴇᴇɴ sᴛᴀʀᴛᴇᴅ! Sᴇɴᴅ ʏᴏᴜʀ ғɪʟᴇs...**")
        message_ids[user_id].append(msg.id)

@Client.on_message(filters.command("esequence") & filters.private)
@check_ban_status
async def end_sequence(client, message: Message):
    user_id = message.from_user.id
    if ADMIN_MODE and user_id not in ADMINS:
        return await message.reply_text("**Aᴅᴍɪɴ ᴍᴏᴅᴇ ɪs ᴀᴄᴛɪᴠᴇ - Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ sᴇǫᴜᴇɴᴄᴇs!**")
    
    if user_id not in active_sequences:
        return await message.reply_text("**Nᴏ ᴀᴄᴛɪᴠᴇ sᴇǫᴜᴇɴᴄᴇ ғᴏᴜɴᴅ!**\n**Usᴇ /ssequence ᴛᴏ sᴛᴀʀᴛ ᴏɴᴇ.**")

    file_list = active_sequences.pop(user_id, [])
    delete_messages = message_ids.pop(user_id, [])

    if not file_list:
        return await message.reply_text("**Nᴏ ғɪʟᴇs ʀᴇᴄᴇɪᴠᴇᴅ ɪɴ ᴛʜɪs sᴇǫᴜᴇɴᴄᴇ!**")

    quality_order = {
        "144p": 1, "240p": 2, "360p": 3, "480p": 4,
        "720p": 5, "1080p": 6, "1440p": 7, "2160p": 8
    }

    def extract_quality(filename):
        filename = filename.lower()
        patterns = [
            (r'2160p|4k', '2160p'),
            (r'1440p|2k', '1440p'),
            (r'1080p|fhd', '1080p'),
            (r'720p|hd', '720p'),
            (r'480p|sd', '480p'),
            (r'(\d{3,4})p', lambda m: f"{m.group(1)}p")
        ]
        
        for pattern, value in patterns:
            match = re.search(pattern, filename)
            if match:
                return value if isinstance(value, str) else value(match)
        return "unknown"

    def sorting_key(f):
        filename = f["file_name"].lower()
        
        season = episode = 0
        season_match = re.search(r's(\d+)', filename)
        episode_match = re.search(r'e(\d+)', filename) or re.search(r'ep?(\d+)', filename)
        
        if season_match:
            season = int(season_match.group(1))
        if episode_match:
            episode = int(episode_match.group(1))
            
        quality = extract_quality(filename)
        quality_priority = quality_order.get(quality.lower(), 9)
        
        padded_episode = f"{episode:04d}"
        
        return (season, padded_episode, quality_priority, filename)

    try:
        sorted_files = sorted(file_list, key=sorting_key)
        await message.reply_text(f"**Sᴇǫᴜᴇɴᴄᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!\nSᴇɴᴅɪɴɢ {len(sorted_files)} ғɪʟᴇs ɪɴ ᴏʀᴅᴇʀ...**")

        for index, file in enumerate(sorted_files):
            try:
                sent_msg = await client.send_document(
                    message.chat.id,
                    file["file_id"],
                    caption=f"**{file['file_name']}**",
                    parse_mode=ParseMode.MARKDOWN
                )

                if Config.DUMP:
                    try:
                        user = message.from_user
                        ist = pytz.timezone('Asia/Kolkata')
                        current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
                        
                        full_name = user.first_name
                        if user.last_name:
                            full_name += f" {user.last_name}"
                        username = f"@{user.username}" if user.username else "N/A"
                        
                        user_data = await DARKXSIDE78.col.find_one({"_id": user_id})
                        is_premium = user_data.get("is_premium", False) if user_data else False
                        premium_status = '🗸' if is_premium else '✘'
                        
                        dump_caption = (
                            f"**» Usᴇʀ Dᴇᴛᴀɪʟs «\n**"
                            f"**ID: {user_id}\n**"
                            f"**Nᴀᴍᴇ: {full_name}\n**"
                            f"**Usᴇʀɴᴀᴍᴇ: {username}\n**"
                            f"**Pʀᴇᴍɪᴜᴍ: {premium_status}\n**"
                            f"**Tɪᴍᴇ: {current_time}\n**"
                            f"**Fɪʟᴇɴᴀᴍᴇ: {file['file_name']}**"
                        )
                        
                        await client.send_document(
                            Config.DUMP_CHANNEL,
                            file["file_id"],
                            caption=dump_caption
                        )
                    except Exception as e:
                        logger.error(f"Dump failed for sequence file: {e}")

                if index < len(sorted_files) - 1:
                    await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except Exception as e:
                logger.error(f"Error sending file {file['file_name']}: {e}")

        if delete_messages:
            await client.delete_messages(message.chat.id, delete_messages)

    except Exception as e:
        logger.error(f"Sequence processing failed: {e}")
        await message.reply_text("**Fᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss sᴇǫᴜᴇɴᴄᴇ! Cʜᴇᴄᴋ ʟᴏɢs ғᴏʀ ᴅᴇᴛᴀɪʟs.**")

@Client.on_message(filters.command("token_usage") & filters.private)
@check_ban_status
async def global_premium_control(client, message: Message):
    global PREMIUM_MODE, PREMIUM_MODE_EXPIRY

    user_id = message.from_user.id
    if user_id not in Config.ADMIN:
        return await message.reply_text("**Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴛᴏ ᴀᴅᴍɪɴs ᴏɴʟʏ!!!**")

    args = message.command[1:]
    if not args:
        status = "ON" if PREMIUM_MODE else "OFF"
        expiry = f" (expires {PREMIUM_MODE_EXPIRY:%Y-%m-%d %H:%M})" if isinstance(PREMIUM_MODE_EXPIRY, datetime) else  ""
        return await message.reply_text(
            f"**➠ Cᴜʀʀᴇɴᴛ Tᴏᴋᴇɴ Usᴀɢᴇ: {status}{expiry}**\n\n"
            "**Usᴀɢᴇ:**\n"
            "`/token_usage on [days|12m|1y]`  — Eɴᴀʙʟᴇ ᴛᴏᴋᴇɴ ᴜsᴀɢᴇ\n"
            "`/token_usage off [days|12m|1y]` — Dɪsᴀʙʟᴇ ᴛᴏᴋᴇɴ ᴜsᴀɢᴇ"
        )

    action = args[0].lower()
    if action not in ("on", "off"):
        return await message.reply_text("**Iɴᴠᴀʟɪᴅ ᴀᴄᴛɪᴏɴ! Usᴇ `on` ᴏʀ `off`**")

    days = None
    if len(args) > 1:
        days = parse_duration(args[1])
        if days is None:
            return await message.reply_text("**Iɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ! Usᴇ 12m, 1y, 30d, 7day, etc.**")

    if action == "on":
        PREMIUM_MODE = True
        PREMIUM_MODE_EXPIRY = datetime.now() + timedelta(days=days) if days else None
        msg = f"**Tᴏᴋᴇɴ ᴜsᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ{f' ғᴏʀ {days} ᴅᴀʏs' if days else ''}**"
    else:
        PREMIUM_MODE = False
        PREMIUM_MODE_EXPIRY = datetime.now() + timedelta(days=days) if days else None
        msg = f"**Tᴏᴋᴇɴ ᴜsᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ{f' ғᴏʀ {days} ᴅᴀʏs' if days else ''}**"

    await DARKXSIDE78.global_settings.update_one(
        {"_id": "premium_mode"},
        {"$set": {"status": PREMIUM_MODE, "expiry": PREMIUM_MODE_EXPIRY}},
        upsert=True
    )
    await message.reply_text(msg)

async def check_premium_mode():
    global PREMIUM_MODE, PREMIUM_MODE_EXPIRY

    settings = await DARKXSIDE78.global_settings.find_one({"_id": "premium_mode"})
    if not settings:
        return

    PREMIUM_MODE        = settings.get("status", True)
    PREMIUM_MODE_EXPIRY = settings.get("expiry", None)

    if PREMIUM_MODE_EXPIRY and isinstance(PREMIUM_MODE_EXPIRY, datetime) and datetime.now() > PREMIUM_MODE_EXPIRY:
        PREMIUM_MODE = False  # Changed to disable premium mode on expiry
        PREMIUM_MODE_EXPIRY = None
        await DARKXSIDE78.global_settings.update_one(
            {"_id": "premium_mode"},
            {"$set": {"status": PREMIUM_MODE, "expiry": PREMIUM_MODE_EXPIRY}}

        )


SEASON_EPISODE_PATTERNS = [
    (re.compile(r'\[S(\d{1,2})[\s\-]+E(\d{1,3})\]', re.IGNORECASE), ('season', 'episode')),   # [S01-E06]
    (re.compile(r'\[S(\d{1,2})[\s\-]+(\d{1,3})\]', re.IGNORECASE), ('season', 'episode')),     # [S01-06]
    (re.compile(r'\[S(\d{1,2})\s+E(\d{1,3})\]', re.IGNORECASE), ('season', 'episode')),        # [S01 E06]
    (re.compile(r'\[S\s*(\d{1,2})\s*E\s*(\d{1,3})\]', re.IGNORECASE), ('season', 'episode')), # [S 1 E 1]
    (re.compile(r'S(\d{1,2})[\s\-]+E(\d{1,3})', re.IGNORECASE), ('season', 'episode')),        # S01-E06, S01 E06
    (re.compile(r'S(\d{1,2})[\s\-]+(\d{1,3})', re.IGNORECASE), ('season', 'episode')),         # S01-06, S01 06
    (re.compile(r'S(\d+)(?:E|EP)(\d+)'), ('season', 'episode')),
    (re.compile(r'S(\d+)[\s-]*(?:E|EP)(\d+)'), ('season', 'episode')),
    (re.compile(r'Season\s*(\d+)\s*Episode\s*(\d+)', re.IGNORECASE), ('season', 'episode')),
    (re.compile(r'\[S(\d+)\]\[E(\d+)\]'), ('season', 'episode')),
    (re.compile(r'S(\d+)[^\d]+(\d{1,3})\b'), ('season', 'episode')),
    (re.compile(r'(?:E|EP|Episode)\s*(\d+)', re.IGNORECASE), (None, 'episode')),
    (re.compile(r'\b(\d{1,3})\b'), (None, 'episode'))
]

QUALITY_PATTERNS = [
    (re.compile(r'\[(\d{3,4}p)\](?:\s*\[\1\])*', re.IGNORECASE), lambda m: m.group(1)),
    (re.compile(r'\b(\d{3,4})p?\b'), lambda m: f"{m.group(1)}p"),
    (re.compile(r'\b(4k|2160p)\b', re.IGNORECASE), lambda m: "2160p"),
    (re.compile(r'\b(2k|1440p)\b', re.IGNORECASE), lambda m: "1440p"),
    (re.compile(r'\b(\d{3,4}[pi])\b', re.IGNORECASE), lambda m: m.group(1)),
    (re.compile(r'\b(HDRip|HDTV)\b', re.IGNORECASE), lambda m: m.group(1)),
    (re.compile(r'\b(4kX264|4kx265)\b', re.IGNORECASE), lambda m: m.group(1)),
    (re.compile(r'\[(\d{3,4}[pi])\]', re.IGNORECASE), lambda m: m.group(1))
]
# Add these patterns at the top of your code with other constants
TITLE_CLEANING_PATTERNS = [
    r'@\w+',
    r'\[?S\d{1,2}[\s\-]*E\d{1,3}\]?', r'Season\s*\d{1,2}', r'Episode\s*\d{1,3}',
    r'\d{1,2}x\d{1,3}', r'EP?\d{1,3}', r'\[\d{1,3}\]',
    r'\[\d{3,4}[pi]\]', r'\d{3,4}p', r'4[kK]', r'2[kK]', 
    r'HDTV', r'WEB[\- ]?DL', r'WEB[\- ]?Rip', r'Blu[\- ]?Ray',
    r'x\d{3,4}', r'HDR', r'DTS', r'AAC', r'AC3',
    r'\[(Sub|Dub|Dual Audio)\]', r'\[(Tam|Tel|Hin|Mal|Kan|Eng|Jpn)\]',
    r'\[.*?\]', r'\(.*?\)', r'v\d', r'[\-_]', r'\d+MB', r'\d+GB',
    r'\.\w{2,4}$', r'\d+p', r'x\d{3,4}',
]

COMMON_WORDS_TO_REMOVE = [
    'complete', 'full', 'uncut', 'remastered', 'extended',
    'dual', 'multi', 'proper', 'repack', 'rerip',
    'limited', 'special edition', 'directors cut',
    'webdl', 'webrip', 'bluray', 'bdrip', 'brrip',
    'dvdrip', 'hdtv', 'hdr', 'uhd', '4k', '1080p', '720p'
]

def clean_title(raw_title):
    """Clean and format the extracted title"""
    if not raw_title:
        return "Unknown"
    
    # First remove file extension if present
    raw_title = re.sub(r'\.[^\.]+$', '', raw_title)
    
    for pattern in TITLE_CLEANING_PATTERNS:
        raw_title = re.sub(pattern, '', raw_title, flags=re.IGNORECASE)
    
    for word in COMMON_WORDS_TO_REMOVE:
        raw_title = re.sub(rf'\b{word}\b', '', raw_title, flags=re.IGNORECASE)
    
    title = re.sub(r'[^\w\s]', ' ', raw_title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    if not title:
        return "Unknown"
    
    return format_title_case(title)

def format_title_case(title):
    """Properly format title case with exceptions"""
    if not title:
        return ""
    
    lowercase_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on',
        'at', 'to', 'from', 'by', 'of', 'in', 'with', 'as', 'is'
    }
    
    words = title.split()
    if not words:
        return ""
    
    formatted_words = []
    for i, word in enumerate(words):
        if i > 0 and word.lower() in lowercase_words:
            formatted_words.append(word.lower())
        else:
            if "'" in word:
                parts = word.split("'")
                formatted = []
                for part in parts:
                    if part:
                        formatted.append(part[0].upper() + part[1:].lower())
                    else:
                        formatted.append("'")
                formatted_words.append("'".join(formatted))
            else:
                formatted_words.append(word[0].upper() + word[1:].lower())
    
    return ' '.join(formatted_words)

def extract_title_from_filename(filename):
    """Main title extraction function"""
    if not filename:
        return "Unknown"
    
    # Remove extension first
    filename = re.sub(r'\.[^\.]+$', '', filename)
    
    # Try to extract from brackets first
    bracket_match = re.search(r'\[([^\]]+)\]', filename)
    if bracket_match:
        potential_title = bracket_match.group(1)
        if (len(potential_title.split()) > 1 and 
            not any(word in potential_title.lower() for word in COMMON_WORDS_TO_REMOVE)):
            return clean_title(potential_title)
    
    # Try common patterns
    patterns = [
        r'^(.*?)(?:\s*[-_]\s*[\[\(]|\[|\()',  # Before first [ or (
        r'^(.*?)(?:\s+[\[\(]|$)',             # Before first [ or ( or end
        r'^(.*?)(?:\s+\d{3,4}p|$)',           # Before resolution or end
        r'^(.*?)(?:\s+[Ss]\d{1,2}|$)'         # Before season or end
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            potential_title = match.group(1)
            if potential_title and len(potential_title.split()) >= 1:
                return clean_title(potential_title)
    
    # Fallback to cleaning the whole filename
    return clean_title(filename)


def extract_season_episode(filename):
    # Remove only (parentheses), not [brackets]
    filename = re.sub(r'\(.*?\)', ' ', filename)
    
    for pattern, (season_group, episode_group) in SEASON_EPISODE_PATTERNS:
        match = pattern.search(filename)
        if match:
            season = episode = None
            if season_group:
                season = match.group(1).zfill(2) if match.group(1) else "01"
            if episode_group:
                episode = match.group(2 if season_group else 1).zfill(2)
            
            logger.info(f"Extracted season: {season}, episode: {episode} from {filename}")
            return season or "01", episode
    
    logger.warning(f"No season/episode pattern matched for {filename}")
    return "01", None

def extract_quality(filename):
    seen = set()
    quality_parts = []
    
    for pattern, extractor in QUALITY_PATTERNS:
        match = pattern.search(filename)
        if match:
            quality = extractor(match).lower()
            if quality not in seen:
                quality_parts.append(quality)
                seen.add(quality)
                filename = filename.replace(match.group(0), '', 1)
    
    return " ".join(quality_parts) if quality_parts else "Unknown"


async def detect_audio_info(file_path):
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        raise RuntimeError("ffprobe not found in PATH")

    cmd = [
        ffprobe,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        file_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    try:
        info = json.loads(stdout)
        streams = info.get('streams', [])
        
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        sub_streams = [s for s in streams if s.get('codec_type') == 'subtitle']

        japanese_audio = 0
        english_audio = 0
        for audio in audio_streams:
            lang = audio.get('tags', {}).get('language', '').lower()
            if lang in {'ja', 'jpn', 'japanese'}:
                japanese_audio += 1
            elif lang in {'en', 'eng', 'english'}:
                english_audio += 1

        english_subs = len([
            s for s in sub_streams 
            if s.get('tags', {}).get('language', '').lower() in {'en', 'eng', 'english'}
        ])

        return len(audio_streams), len(sub_streams), japanese_audio, english_audio, english_subs
    except Exception as e:
        logger.error(f"Audio detection error: {e}")
        return 0, 0, 0, 0, 0

def get_audio_label(audio_info):
    audio_count, sub_count, jp_audio, en_audio, en_subs = audio_info
    
    if audio_count == 1:
        if jp_audio >= 1 and en_subs >= 1:
            return "Sub" + ("s" if sub_count > 1 else "")
        if en_audio >= 1:
            return "Dub"
    
    if audio_count == 2:
        return "Dual"
    elif audio_count == 3:
        return "Tri"
    elif audio_count >= 4:
        return "Multi"
    
    return "Unknown"

async def detect_video_resolution(file_path):
    """Detect actual video resolution using FFmpeg"""
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        raise RuntimeError("ffprobe not found in PATH")

    cmd = [
        ffprobe,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        '-select_streams', 'v',
        file_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    try:
        info = json.loads(stdout)
        streams = info.get('streams', [])
        
        if not streams:
            return "Unknown"
            
        video_stream = streams[0]
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        
        if height >= 2160 or width >= 3840:
            return "2160p"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        elif height >= 360:
            return "360p"
        elif height >= 240:
            return "240p"
        elif height >= 144:
            return "144p"
        else:
            return f"{height}p"
            
    except Exception as e:
        logger.error(f"Resolution detection error: {e}")
        return "Unknown"

async def process_thumbnail(thumb_path):
    if not thumb_path or not await aiofiles.os.path.exists(thumb_path):
        return None
    try:
        img = await asyncio.to_thread(Image.open, thumb_path)
        img = await asyncio.to_thread(lambda: img.convert("RGB").resize((320, 320)))
        await asyncio.to_thread(img.save, thumb_path, "JPEG")
        return thumb_path
    except Exception as e:
        logger.error(f"Thumbnail processing failed: {e}")
        await cleanup_files(thumb_path)
        return None

async def cleanup_files(*paths):
    for path in paths:
        try:
            if path and await aiofiles.os.path.exists(path):
                await aiofiles.os.remove(path)
        except Exception as e:
            logger.error(f"Error removing {path}: {e}")

async def add_metadata(input_path, output_path, user_id):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found in PATH")

    output_dir = os.path.dirname(output_path)
    await aiofiles.os.makedirs(output_dir, exist_ok=True)

    metadata = {
        'title': await DARKXSIDE78.get_title(user_id),
        'video': await DARKXSIDE78.get_video(user_id),
        'audio': await DARKXSIDE78.get_audio(user_id),
        'subtitle': await DARKXSIDE78.get_subtitle(user_id),
        'artist': await DARKXSIDE78.get_artist(user_id),
        'author': await DARKXSIDE78.get_author(user_id),
        'encoded_by': await DARKXSIDE78.get_encoded_by(user_id),
        'custom_tag': await DARKXSIDE78.get_custom_tag(user_id),
        'commentz': await DARKXSIDE78.get_commentz(user_id)
    }

    cmd = [
        ffmpeg,
        '-hide_banner',
        '-i', input_path,
        '-map', '0',
        '-c', 'copy',
        '-metadata', f'title={metadata["title"]}',
        '-metadata:s:v', f'title={metadata["video"]}',
        '-metadata:s:s', f'title={metadata["subtitle"]}',
        '-metadata:s:a', f'title={metadata["audio"]}',
        '-metadata', f'artist={metadata["artist"]}',
        '-metadata', f'author={metadata["author"]}',
        '-metadata', f'encoded_by={metadata["encoded_by"]}',
        '-metadata', f'comment={metadata["commentz"]}',
        '-metadata', f'custom_tag={metadata["custom_tag"]}',
        '-loglevel', 'error',
        '-y'
    ]

    cmd += ['-f', 'matroska', output_path]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"FFmpeg error: {error_msg}")
            
            if await aiofiles.os.path.exists(output_path):
                await aiofiles.os.remove(output_path)
            
            raise RuntimeError(f"Metadata addition failed: {error_msg}")

        return output_path

    except Exception as e:
        logger.error(f"Metadata processing failed: {e}")
        await cleanup_files(output_path)
        raise

def extract_chapter(filename): 
    """Extract chapter number from filename"""
    if not filename:
        return None

    patterns = [
        r'Ch(\d+)', r'Chapter(\d+)', r'CH(\d+)', 
        r'ch(\d+)', r'Chap(\d+)', r'chap(\d+)',
        r'Ch\.(\d+)', r'Chapter\.(\d+)', r'CH\.(\d+)',
        r'ch\.(\d+)', r'Chap\.(\d+)', r'chap\.(\d+)',
        r'Ch-(\d+)', r'Chapter-(\d+)', r'CH-(\d+)',
        r'ch-(\d+)', r'Chap-(\d+)', r'chap-(\d+)',
        r'CH-(\d+)', r'CHAP-(\d+)', r'CHAPTER (\d+)',
        r'Ch (\d+)', r'Chapter (\d+)', r'CH (\d+)',
        r'ch (\d+)', r'Chap (\d+)', r'chap (\d+)',
        r'\[Ch(\d+)\]', r'\[Chapter(\d+)\]', r'\[CH(\d+)\]',
        r'\[ch(\d+)\]', r'\[Chap(\d+)\]', r'\[chap(\d+)\]',
        r'\[C(\d+)\]'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1).zfill(2)
    
    return None

def extract_volume(filename):
    """Extract volume number from filename"""
    if not filename:
        return None

    patterns = [
        r'\[V(?:ol(?:ume)?)?[._ -]?(\d+)\]',
        r'V(?:ol(?:ume)?)?[._ -]?(\d+)',
        r'\bvol(?:ume)?[._ -]?(\d+)\b',
        r'\bvol(?:ume)?\s*(\d+)\b',
        r'\(vol(?:ume)?[._ -]?(\d+)\)',
        r'\bV\s*[\.:_-]?\s*(\d+)\b',
        r'\bVol\s*[\.:_-]?\s*(\d+)\b',
        r'\bVolume\s*[\.:_-]?\s*(\d+)\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1).zfill(2)

    return None

async def convert_to_mkv(input_path, output_path):
    """Convert video file to MKV format"""
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found in PATH")

    cmd = [
        ffmpeg,
        '-hide_banner',
        '-i', input_path,
        '-map', '0',
        '-c', 'copy',
        '-f', 'matroska',
        '-y',
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        raise RuntimeError(f"MKV conversion failed: {error_msg}")
    
    return output_path

# Update the auto_rename_files function to include title extraction
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
@check_ban_status
async def auto_rename_files(client, message: Message):
    user_id = message.from_user.id
    user = message.from_user

    if ADMIN_MODE and user_id not in ADMINS:
        return await message.reply_text("Aᴅᴍɪɴ ᴍᴏᴅᴇ ɪs ᴀᴄᴛɪᴠᴇ - Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!")
    autorename_enabled = await DARKXSIDE78.get_autorename_status(user_id)
    if not autorename_enabled:
        return await message.reply_text("🔕 Auto-Rename is turned OFF.\nUse /autorename_on to enable it.")

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = "document"
        file_ext = os.path.splitext(file_name)[1].lower() if file_name else None
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video"
        media_type = "video"
        file_ext = ".mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio"
        media_type = "audio"
        file_ext = None
    else:
        return await message.reply_text("**Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ᴛʏᴘᴇ**")
        
    if user_id in active_sequences:
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
        elif message.video:
            file_id = message.video.file_id
            file_name = f"{message.video.file_name}.mp4"
        elif message.audio:
            file_id = message.audio.file_id
            file_name = f"{message.audio.file_name}.mp3"

        file_info = {"file_id": file_id, "file_name": file_name if file_name else "Unknown"}
        active_sequences[user_id].append(file_info)
        await message.reply_text("Fɪʟᴇ ʀᴇᴄᴇɪᴠᴇᴅ ɪɴ sᴇǫᴜᴇɴᴄᴇ...\nEɴᴅ Sᴇǫᴜᴇɴᴄᴇ ʙʏ ᴜsɪɴɢ /esequence")
        return
        
    async def process_file():
        nonlocal file_id, file_name, media_type, file_ext
        file_path = None
        download_path = None
        metadata_path = None
        thumb_path = None
        output_path = None

        try:
            media_preference = await DARKXSIDE78.get_media_preference(user_id)
            user_data = await DARKXSIDE78.col.find_one({"_id": user_id})
            is_premium = user_data.get("is_premium", False) if user_data else False
            is_admin = hasattr(Config, "ADMIN") and user_id in Config.ADMIN
            
            premium_expiry = user_data.get("premium_expiry")
            if is_premium and premium_expiry:
                if datetime.now() < premium_expiry:
                    is_premium = True
                else:
                    await DARKXSIDE78.col.update_one(
                        {"_id": user_id},
                        {"$set": {"is_premium": False, "premium_expiry": None}}
                    )
                    is_premium = False

            if not is_premium:
                current_tokens = user_data.get("token", Config.DEFAULT_TOKEN)
                if current_tokens <= 0:
                    await message.reply_text("**Yᴏᴜ'ᴠᴇ ʀᴜɴ ᴏᴜᴛ ᴏғ ᴛᴏᴋᴇɴs!\nGᴇɴᴇʀᴀᴛᴇ ᴍᴏʀᴇ ʙʏ ᴜsɪɴɢ /gentoken ᴄᴍᴅ.**")
                    return
            
            if PREMIUM_MODE and not is_premium:
                current_tokens = user_data.get("token", 0)
                if current_tokens <= 0:
                    return await message.reply_text("**Yᴏᴜ'ᴠᴇ ʀᴜɴ ᴏᴜᴛ ᴏғ ᴛᴏᴋᴇɴs!\nGᴇɴᴇʀᴀᴛᴇ ᴍᴏʀᴇ ʙʏ ᴜsɪɴɢ /gentoken ᴄᴍᴅ.**")
                await DARKXSIDE78.col.update_one(
                    {"_id": user_id},
                    {"$inc": {"token": -1}}
                )
            
            format_template = await DARKXSIDE78.get_format_template(user_id)
            media_preference = await DARKXSIDE78.get_media_preference(user_id)
            metadata_source = await DARKXSIDE78.get_metadata_source(user_id)
            
            if metadata_source == "caption" and message.caption:
                source_text = message.caption
            else:
                source_text = file_name
            
            # Extract all metadata components
            season, episode = extract_season_episode(source_text)
            chapter = extract_chapter(source_text)
            volume = extract_volume(source_text)
            quality = extract_quality(source_text)
            title = extract_title_from_filename(source_text)

            if not format_template:
                return await message.reply_text("**Aᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ ɴᴏᴛ sᴇᴛ\nPʟᴇᴀsᴇ sᴇᴛ ᴀ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ ᴜsɪɴɢ /autorename**")

            if file_id in renaming_operations:
                elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
                if elapsed_time < 10:
                    return

            renaming_operations[file_id] = datetime.now()
            
            msg = await message.reply_text("**Pʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...**")
            
            try:
                audio_label = ""
                
                if media_type == "video" and media_preference == "document":
                    ext = ".mkv"
                elif media_type == "document" and media_preference == "video":
                    ext = ".mp4"
                elif file_ext and file_ext.lower() == ".pdf":
                    ext = ".pdf"
                else:
                    ext = os.path.splitext(file_name)[1] or ('.mp4' if media_type == 'video' else '.mp3')
                
                download_path = f"downloads/{file_name}"
                metadata_path = f"metadata/{file_name}"
                output_path = f"processed/{os.path.splitext(file_name)[0]}{ext}"
                
                await aiofiles.os.makedirs(os.path.dirname(download_path), exist_ok=True)
                await aiofiles.os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                await aiofiles.os.makedirs(os.path.dirname(output_path), exist_ok=True)

                await msg.edit("**Dᴏᴡɴʟᴏᴀᴅɪɴɢ...**")
                try:
                    file_path = await client.download_media(
                        message,
                        file_name=download_path,
                        progress=progress_for_pyrogram,
                        progress_args=("**Dᴏᴡɴʟᴏᴀᴅɪɴɢ...**", msg, time.time())
                    )
                except Exception as e:
                    await msg.edit(f"Dᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ: {e}")
                    raise
                
                await asyncio.sleep(1)
                await msg.edit("**Dᴏᴡɴʟᴏᴀᴅɪɴɢ Cᴏᴍᴘʟᴇᴛᴇ**")
                audio_info = await detect_audio_info(file_path)
                audio_label = get_audio_label(audio_info)
                actual_resolution = await detect_video_resolution(file_path)

                replacements = {
                    '{title}': title,
                    '{Title}': title,
                    '{TITLE}': title.upper(),
                    '{season}': season or 'XX',
                    '{episode}': episode or 'XX',
                    '{chapter}': chapter or 'XX',
                    '{volume}': volume or 'XX',
                    '{quality}': quality,
                    '{audio}': audio_label,
                    '{Season}': season or 'XX',
                    '{Episode}': episode or 'XX',
                    '{Chapter}': chapter or 'XX',
                    '{Volume}': volume or 'XX',
                    '{Quality}': quality,
                    '{Audio}': audio_label,
                    '{SEASON}': season or 'XX',
                    '{EPISODE}': episode or 'XX',
                    '{CHAPTER}': chapter or 'XX',
                    '{VOLUME}': volume or 'XX',
                    '{QUALITY}': quality,
                    '{AUDIO}': audio_label,
                    'Season': season or 'XX',
                    'Episode': episode or 'XX',
                    'Chapter': chapter or 'XX',
                    'Volume': volume or 'XX',
                    'Quality': quality,
                    'Audio': audio_label,
                    'SEASON': season or 'XX',
                    'EPISODE': episode or 'XX',
                    'CHAPTER': chapter or 'XX',
                    'VOLUME': volume or 'XX',
                    'QUALITY': quality,
                    'AUDIO': audio_label,
                    'season': season or 'XX',
                    'episode': episode or 'XX',
                    'chapter': chapter or 'XX',
                    'volume': volume or 'XX',
                    'quality': quality,
                    'audio': audio_label,
                    '{resolution}': actual_resolution,
                    '{Resolution}': actual_resolution,
                    '{RESOLUTION}': actual_resolution,
                    'resolution': actual_resolution,
                    'Resolution': actual_resolution,
                    'RESOLUTION': actual_resolution,
                }
                
                # Apply all replacements to the format template
                new_filename = format_template
                for placeholder, value in replacements.items():
                    new_filename = new_filename.replace(placeholder, value)
                
                new_filename = re.sub(r'[<>:"/\\|?*]', '', new_filename)  # Remove invalid filename characters
                new_filename = re.sub(r'\s+', ' ', new_filename).strip()  # Clean up whitespace
                
                new_download = os.path.join("downloads", new_filename)
                new_metadata = os.path.join("metadata", new_filename)
                new_output = os.path.join("processed", new_filename)

                await aiofiles.os.rename(download_path, new_download)
                download_path = new_download
                metadata_path = new_metadata
                output_path = new_output

                await msg.edit("**Pʀᴏᴄᴇssɪɴɢ ғɪʟᴇ...**")
                
                if media_type == "video" and media_preference == "document":
                    try:
                        await convert_to_mkv(download_path, output_path)
                        file_path = output_path
                    except Exception as e:
                        await msg.edit(f"Vɪᴅᴇᴏ ᴄᴏɴᴠᴇʀsɪᴏɴ ғᴀɪʟᴇᴅ: {e}")
                        raise
                else:
                    file_path = download_path

                if (media_type in ["video", "audio"] or 
                    (media_type == "document" and file_ext != ".pdf")):
                    try:
                        await msg.edit("**Aᴅᴅɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ...**")
                        await add_metadata(
                            file_path if media_type == "video" else download_path,
                            metadata_path, 
                            user_id
                        )
                        file_path = metadata_path
                    except Exception as e:
                        await msg.edit(f"Mᴇᴛᴀᴅᴀᴛᴀ ғᴀɪʟᴇᴅ: {e}")
                        raise
                else:
                    if media_type == "document" and file_ext == ".pdf":
                        pdf_banner_on = await DARKXSIDE78.get_pdf_banner_mode(user_id)
                        pdf_banner_file = await DARKXSIDE78.get_pdf_banner(user_id)
                        pdf_lock_on = await DARKXSIDE78.get_pdf_lock_mode(user_id)
                        pdf_lock_password = await DARKXSIDE78.get_pdf_lock_password(user_id)
                        pdf_banner_placement = await DARKXSIDE78.get_pdf_banner_placement(user_id) or "first"

                        if pdf_banner_on and pdf_banner_file:
                            try:
                                temp_banner_path = f"{download_path}_banner.jpg"
                                await client.download_media(pdf_banner_file, file_name=temp_banner_path)
                                reader = PdfReader(download_path)
                                writer = PdfWriter()
                                img = Image.open(temp_banner_path).convert("RGB")
                                img_pdf_path = temp_banner_path + ".pdf"
                                img.save(img_pdf_path, "PDF")
                                img_reader = PdfReader(img_pdf_path)
                                img_page = img_reader.pages[0]
                                if pdf_banner_placement == "first":
                                    writer.add_page(img_page)
                                    for page in reader.pages:
                                        writer.add_page(page)
                                elif pdf_banner_placement == "last":
                                    for page in reader.pages:
                                        writer.add_page(page)
                                    writer.add_page(img_page)
                                elif pdf_banner_placement == "both":
                                    writer.add_page(img_page)
                                    for page in reader.pages:
                                        writer.add_page(page)
                                    writer.add_page(img_page)
                                else:
                                    writer.add_page(img_page)
                                    for page in reader.pages:
                                        writer.add_page(page)
                                bannered_pdf_path = download_path.replace(".pdf", "_bannered.pdf")
                                with open(bannered_pdf_path, "wb") as f:
                                    writer.write(f)
                                await cleanup_files(download_path, temp_banner_path, img_pdf_path)
                                download_path = bannered_pdf_path
                            except Exception as e:
                                logger.error(f"Auto PDF banner failed: {e}")

                        if pdf_lock_on and pdf_lock_password:
                            try:
                                reader = PdfReader(download_path)
                                writer = PdfWriter()
                                for page in reader.pages:
                                    writer.add_page(page)
                                writer.encrypt(pdf_lock_password)
                                locked_pdf_path = download_path.replace(".pdf", "_locked.pdf")
                                with open(locked_pdf_path, "wb") as f:
                                    writer.write(f)
                                await cleanup_files(download_path)
                                download_path = locked_pdf_path
                            except Exception as e:
                                logger.error(f"Auto PDF lock failed: {e}")

                        file_path = download_path
                        await aiofiles.os.rename(download_path, output_path)
                        file_path = output_path

                await msg.edit("**Pʀᴇᴘᴀʀɪɴɢ ᴜᴘʟᴏᴀᴅ...**")
                await DARKXSIDE78.col.update_one(
                    {"_id": user_id},
                    {
                        "$inc": {
                            "rename_count": 1,
                            "total_renamed_size": message.document.file_size if media_type == "document" else 
                                                 message.video.file_size if media_type == "video" else 
                                                 message.audio.file_size,
                            "daily_count": 1
                        },
                        "$max": {
                            "max_file_size": message.document.file_size if media_type == "document" else 
                                            message.video.file_size if media_type == "video" else 
                                            message.audio.file_size
                        }
                    }
                )

                caption = await DARKXSIDE78.get_caption(message.chat.id) or f"**{new_filename}**"
                thumb = await DARKXSIDE78.get_thumbnail(message.chat.id)
                thumb_path = None

                if thumb:
                    thumb_path = await client.download_media(thumb)
                elif media_type == "video" and message.video.thumbs:
                    thumb_path = await client.download_media(message.video.thumbs[0].file_id)

                await msg.edit("**Uᴘʟᴏᴀᴅɪɴɢ...**")
                try:
                    upload_params = {
                        'chat_id': message.chat.id,
                        'caption': caption,
                        'thumb': thumb_path,
                        'progress': progress_for_pyrogram,
                        'progress_args': ("Uᴘʟᴏᴀᴅɪɴɢ...", msg, time.time())
                    }

                    if file_ext in (
                        ".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                        ".odt", ".rtf", ".csv", ".epub", ".mobi", ".zip", ".rar", ".7z",
                        ".xml", ".html", ".json", ".md", ".log", ".ini", ".bat", ".sh"
                    ):
                        await client.send_document(
                        document=file_path,
                        **upload_params
                        )
                    elif media_type == "video":
                        if media_preference == "video":
                            await client.send_video(
                                video=file_path,
                                **upload_params
                            )
                        else:
                            await client.send_document(
                                document=file_path,
                                force_document=True,
                                **upload_params
                            )
                    elif media_type == "document":
                        if media_preference == "video":
                            await client.send_video(
                                video=file_path,
                                **upload_params
                            )
                        else:
                            await client.send_document(
                                document=file_path,
                                **upload_params
                            )
                    elif media_type == "audio":
                        await client.send_audio(
                            audio=file_path,
                            **upload_params
                        )
                    new_file_name = new_filename

                    await DARKXSIDE78.add_rename_history(user_id, original_name=file_name, renamed_name=new_file_name)

                    if Config.DUMP:
                        try:
                            ist = pytz.timezone('Asia/Kolkata')
                            current_time = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
                            
                            full_name = user.first_name
                            if user.last_name:
                                full_name += f" {user.last_name}"
                            username = f"@{user.username}" if user.username else "N/A"
                            premium_status = '🗸' if is_premium else '✘'
                            
                            dump_caption = (
                                f"» Usᴇʀ Dᴇᴛᴀɪʟs «\n"
                                f"ID: {user_id}\n"
                                f"Nᴀᴍᴇ: {full_name}\n"
                                f"Usᴇʀɴᴀᴍᴇ: {username}\n"
                                f"Pʀᴇᴍɪᴜᴍ: {premium_status}\n"
                                f"Tɪᴍᴇ: {current_time}\n"
                                f"Oʀɪɢɪɴᴀʟ Fɪʟᴇɴᴀᴍᴇ: {file_name}\n"
                                f"Rᴇɴᴀᴍᴇᴅ Fɪʟᴇɴᴀᴍᴇ: {new_filename}"
                            )
                            
                            dump_channel = Config.DUMP_CHANNEL
                            await asyncio.sleep(1.2)
                            if media_type == "document":
                                await client.copy_message(
                                    chat_id=dump_channel,
                                    from_chat_id=message.chat.id,
                                    message_id=message.id,
                                    caption=dump_caption
                                )
                            elif media_type == "video":
                                await client.copy_message(
                                    chat_id=dump_channel,
                                    from_chat_id=message.chat.id,
                                    message_id=message.id,
                                    caption=dump_caption
                                )
                            elif media_type == "audio":
                                await client.copy_message(
                                    chat_id=dump_channel,
                                    from_chat_id=message.chat.id,
                                    message_id=message.id,
                                    caption=dump_caption
                                )
                        except Exception as e:
                            logger.error(f"Error sending to dump channel: {e}")

                    await msg.delete()
                except Exception as e:
                    await msg.edit(f"Uᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ: {e}")
                    raise

            except Exception as e:
                logger.error(f"Processing error: {e}")
                await message.reply_text(f"Eʀʀᴏʀ: {str(e)}")
            finally:
                await cleanup_files(download_path, metadata_path, thumb_path, output_path)
                renaming_operations.pop(file_id, None)
                
        except asyncio.CancelledError:
            logger.info(f"Task for file {file_id} was cancelled")
            if file_path or download_path or metadata_path or thumb_path or output_path:
                await cleanup_files(download_path, metadata_path, thumb_path, output_path)
            renaming_operations.pop(file_id, None)
            raise
    
    status = await task_queue.get_queue_status(user_id)
    msg = await message.reply_text(
        f"**Yᴏᴜʀ ꜰɪʟᴇ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ qᴜᴇᴜᴇ {status['processing']}. Pʟᴇᴀsᴇ Wᴀɪᴛ.......**"
    )
    
    await task_queue.add_task(user_id, file_id, message, process_file())
    
@Client.on_message(filters.command("renamed") & (filters.group | filters.private))
@check_ban_status
async def renamed_stats(client, message: Message):
    try:
        args = message.command[1:] if len(message.command) > 1 else []
        target_user = None
        requester_id = message.from_user.id
        time_filter = "lifetime"
        
        requester_data = await DARKXSIDE78.col.find_one({"_id": requester_id})
        is_premium = requester_data.get("is_premium", False) if requester_data else False
        is_admin = requester_id in Config.ADMIN if Config.ADMIN else False

        if is_premium and requester_data.get("premium_expiry"):
            if datetime.now() > requester_data["premium_expiry"]:
                is_premium = False
                await DARKXSIDE78.col.update_one(
                    {"_id": requester_id},
                    {"$set": {"is_premium": False}}
                )

        if args:
            try:
                if args[0].startswith("@"):
                    user = await client.get_users(args[0])
                    target_user = user.id
                else:
                    target_user = int(args[0])
            except:
                await message.reply_text("**Iɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ! Usᴇ /renamed [@username|user_id]**")
                return

        if target_user and not (is_admin or is_premium):
            return await message.reply_text("**Pʀᴇᴍɪᴜᴍ ᴏʀ ᴀᴅᴍɪɴ ʀᴇǫᴜɪʀᴇᴅ ᴛᴏ ᴠɪᴇᴡ ᴏᴛʜᴇʀs' sᴛᴀᴛs!**")

        await show_stats(client, message, target_user, time_filter, is_admin, is_premium, requester_id)

    except Exception as e:
        error_msg = await message.reply_text(f"❌ Error: {str(e)}")
        await asyncio.sleep(30)
        await error_msg.delete()
        logger.error(f"Stats error: {e}", exc_info=True)

async def show_stats(client, message, target_user, time_filter, is_admin, is_premium, requester_id):
    try:
        now = datetime.now()
        date_filter = None
        period_text = "Lɪғᴇᴛɪᴍᴇ"
        
        if time_filter == "today":
            date_filter = {"$gte": datetime.combine(now.date(), datetime.min.time())}
            period_text = "Tᴏᴅᴀʏ"
        elif time_filter == "week":
            start_of_week = now - timedelta(days=now.weekday())
            date_filter = {"$gte": datetime.combine(start_of_week.date(), datetime.min.time())}
            period_text = "Tʜɪs Wᴇᴇᴋ"
        elif time_filter == "month":
            start_of_month = datetime(now.year, now.month, 1)
            date_filter = {"$gte": start_of_month}
            period_text = "Tʜɪs Mᴏɴᴛʜ"
        elif time_filter == "year":
            start_of_year = datetime(now.year, 1, 1)
            date_filter = {"$gte": start_of_year}
            period_text = "Tʜɪs Yᴇᴀʀ"
        
        if target_user:
            user_data = await DARKXSIDE78.col.find_one({"_id": target_user})
            if not user_data:
                return await message.reply_text("**Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!**")
            
            if date_filter:
                rename_logs = await DARKXSIDE78.rename_logs.find({
                    "user_id": target_user,
                    "timestamp": date_filter
                }).to_list(length=None)
                
                rename_count = len(rename_logs)
                total_renamed_size = sum(log.get("file_size", 0) for log in rename_logs)
                max_file_size = max([log.get("file_size", 0) for log in rename_logs] or [0])
            else:
                rename_count = user_data.get('rename_count', 0)
                total_renamed_size = user_data.get('total_renamed_size', 0)
                max_file_size = user_data.get('max_file_size', 0)

            response = [
                f"**┌─── ∘° {period_text} Sᴛᴀᴛs °∘ ───┐**",
                f"**➤ Usᴇʀ: {target_user}**",
                f"**➤ Tᴏᴛᴀʟ Rᴇɴᴀᴍᴇs: {rename_count}**",
                f"**➤ Tᴏᴛᴀʟ Sɪᴢᴇ: {humanbytes(total_renamed_size)}**",
                f"**➤ Mᴀx Fɪʟᴇ Sɪᴢᴇ: {humanbytes(max_file_size)}**",
                f"**➤ Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs: {'Active' if user_data.get('is_premium') else 'Inactive'}**"
            ]
            
            if is_admin or is_premium:
                response.append(f"**➤ Tᴏᴋᴇɴs: {user_data.get('token', 0)}**")
                response.append(f"**└───────── °∘ ❉ ∘° ───────┘**")

        else:
            user_data = await DARKXSIDE78.col.find_one({"_id": requester_id})
            if not user_data:
                user_data = {}
                
            if date_filter:
                rename_logs = await DARKXSIDE78.rename_logs.find({
                    "user_id": requester_id,
                    "timestamp": date_filter
                }).to_list(length=None)
                
                rename_count = len(rename_logs)
                total_renamed_size = sum(log.get("file_size", 0) for log in rename_logs)
                max_file_size = max([log.get("file_size", 0) for log in rename_logs] or [0])
            else:
                rename_count = user_data.get('rename_count', 0)
                total_renamed_size = user_data.get('total_renamed_size', 0)
                max_file_size = user_data.get('max_file_size', 0)
                
            response = [
                f"**┌─── ∘° Yᴏᴜʀ {period_text} Sᴛᴀᴛs °∘ ───┐**",
                f"**➤ Tᴏᴛᴀʟ Rᴇɴᴀᴍᴇs: {rename_count}**",
                f"**➤ Tᴏᴛᴀʟ Sɪᴢᴇ: {humanbytes(total_renamed_size)}**",
                f"**➤ Mᴀx Fɪʟᴇ Sɪᴢᴇ: {humanbytes(max_file_size)}**",
                f"**➤ Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs: {'Active' if is_premium else 'Inactive'}**",
                f"**➤ Rᴇᴍᴀɪɴɪɴɢ Tᴏᴋᴇɴs: {user_data.get('token', 0)}**",
                f"**└──────── °∘ ❉ ∘° ─────────┘**"
            ]

            if (is_admin or is_premium) and time_filter == "lifetime":
                pipeline = [{"$group": {
                    "_id": None,
                    "total_renames": {"$sum": "$rename_count"},
                    "total_size": {"$sum": "$total_renamed_size"},
                    "max_size": {"$max": "$max_file_size"},
                    "user_count": {"$sum": 1}
                }}]
                stats = (await DARKXSIDE78.col.aggregate(pipeline).to_list(1))[0]
                
                response.extend([
                    f"\n<blockquote>**┌─── ∘° Gʟᴏʙᴀʟ Sᴛᴀᴛs °∘ ───┐**</blockquote>",
                    f"**➤ Tᴏᴛᴀʟ Usᴇʀs: {stats['user_count']}**",
                    f"**➤ Tᴏᴛᴀʟ Fɪʟᴇs: {stats['total_renames']}**",
                    f"**➤ Tᴏᴛᴀʟ Sɪᴢᴇ: {humanbytes(stats['total_size'])}**",
                    f"**➤ Lᴀʀɢᴇsᴛ Fɪʟᴇ: {humanbytes(stats['max_size'])}**",
                    f"**<blockquote>**└─────── °∘ ❉ ∘° ────────┘**</blockquote>**"
                ])

        reply = await message.reply_text("\n".join(response))
        
        if message.chat.type != "private":
            await asyncio.sleep(Config.RENAMED_DELETE_TIMER)
            await reply.delete()
            await message.delete()

    except Exception as e:
        error_msg = await message.reply_text(f"❌ Error: {str(e)}")
        await asyncio.sleep(30)
        await error_msg.delete()
        logger.error(f"Stats error: {e}", exc_info=True)

@Client.on_callback_query(filters.regex(r"^renamed_filter:"))
async def renamed_filter_callback(client, callback_query):
    try:
        data_parts = callback_query.data.split(":")
        time_filter = data_parts[1]
        user_id = int(data_parts[2])
        
        requester_id = callback_query.from_user.id
        
        requester_data = await DARKXSIDE78.col.find_one({"_id": requester_id})
        is_premium = requester_data.get("is_premium", False) if requester_data else False
        is_admin = requester_id in Config.ADMIN if Config.ADMIN else False
        
        target_user = None
        if user_id != requester_id:
            if is_admin or is_premium:
                target_user = user_id
            else:
                await callback_query.answer("Yᴏᴜ ᴄᴀɴɴᴏᴛ ᴠɪᴇᴡ ᴏᴛʜᴇʀ ᴜsᴇʀs' sᴛᴀᴛs!", show_alert=True)
                return
        
        await show_stats(client, callback_query.message, target_user, time_filter, is_admin, is_premium, requester_id)
        
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
        logger.error(f"Callback error: {e}", exc_info=True)

@Client.on_message(filters.command("info") & (filters.group | filters.private))
@check_ban_status
async def system_info(client, message: Message):
    try:
        import psutil
        from platform import python_version, system, release

        total_users = await DARKXSIDE78.col.count_documents({})
        active_30d = await DARKXSIDE78.col.count_documents({
            "last_active": {"$gte": datetime.now() - timedelta(days=30)}
        })
        active_24h = await DARKXSIDE78.col.count_documents({
            "last_active": {"$gte": datetime.now() - timedelta(hours=24)}
        })
        
        storage_pipeline = [
            {"$group": {
                "_id": None,
                "total_size": {"$sum": "$total_renamed_size"},
                "total_files": {"$sum": "$rename_count"}
            }}
        ]
        storage_stats = await DARKXSIDE78.col.aggregate(storage_pipeline).to_list(1)
        
        cpu_usage = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        
        response = f"""
<blockquote>╒══════════════**「 🔍 Sʏsᴛᴇᴍ Iɴғᴏ 」**══════════════╕</blockquote>


<blockquote>┍─**[Usᴇʀ Sᴛᴀᴛɪsᴛɪᴄs]**
├─**Tᴏᴛᴀʟ Usᴇʀs = {total_users:,}**
├─**Tᴏᴛᴀʟ Fɪʟᴇs Rᴇɴᴀᴍᴇᴅ = {storage_stats[0].get('total_files', 0) if storage_stats else 0}**
┕─**Tᴏᴛᴀʟ Sᴛᴏʀᴀɢᴇ Usᴇᴅ = {humanbytes(storage_stats[0].get('total_size', 0)) if storage_stats else '0 B'}**</blockquote>

<blockquote>┍─**[Sʏsᴛᴇᴍ Iɴғᴏʀᴍᴀᴛɪᴏɴ]**
├─**OS Vᴇʀsɪᴏɴ = {system()} {release()}**
├─**Pʏᴛʜᴏɴ Vᴇʀsɪᴏɴ = {python_version()}**
├─**CPU Usᴀɢᴇ = {cpu_usage}%**
├─**Mᴇᴍᴏʀʏ Usᴀɢᴇ = {humanbytes(mem.used)} / {humanbytes(mem.total)}**
├─**Dɪsᴋ Usᴀɢᴇ = {humanbytes(disk.used)} / {humanbytes(disk.total)}**
┕─**Uᴘᴛɪᴍᴇ = {datetime.now() - datetime.fromtimestamp(psutil.boot_time())}**</blockquote>

<blockquote>┍─**[Vᴇʀsɪᴏɴ Iɴғᴏʀᴍᴀᴛɪᴏɴ]**
├─**Bᴏᴛ Vᴇʀsɪᴏɴ = ****{Config.VERSION}**
├─**Lᴀsᴛ Uᴘᴅᴀᴛᴇᴅ = ****{Config.LAST_UPDATED}**
┕─**Dᴀᴛᴀʙᴀsᴇ Vᴇʀsɪᴏɴ =** **{Config.DB_VERSION}**</blockquote>

<blockquote>╘══════════════**「 {Config.BOT_NAME} 」**══════════════╛</blockquote>
    """
        await message.reply_text(response)

    except Exception as e:
        await message.reply_text(f"Eʀʀᴏʀ: {str(e)}")
        logger.error(f"System info error: {e}", exc_info=True)

@Client.on_message(filters.command("set_pdf_banner_place"))
@check_ban_status
async def set_pdf_banner_place_cmd(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].strip().lower() not in ("first", "last", "both"):
        return await message.reply(
            "**Usᴀɢᴇ:** `/set_pdf_banner_place first|last|both`\n"
            "**Sᴇᴛ ᴡʜᴇʀᴇ ʏᴏᴜʀ PDF ʙᴀɴɴᴇʀ ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ʙʏ ᴅᴇғᴀᴜʟᴛ.**"
        )
    placement = args[1].strip().lower()
    await DARKXSIDE78.set_pdf_banner_placement(message.from_user.id, placement)
    await message.reply(f"**PDF ʙᴀɴɴᴇʀ ᴘʟᴀᴄᴇᴍᴇɴᴛ sᴇᴛ ᴛᴏ:** `{placement}`")

@Client.on_message(
    filters.command(["mode_pdf", "modepdf", "pdfmode", "pdf_mode"]) & (filters.private | filters.group)
)
@check_ban_status
async def pdf_mode_settings(client, message, edit=False, user_id=None):
    if user_id is None:
        user_id = getattr(message, "from_user", None)
        if user_id:
            user_id = user_id.id
        else:
            user_id = message.chat.id

    pdf_banner_on = await DARKXSIDE78.get_pdf_banner_mode(user_id)
    pdf_banner_file = await DARKXSIDE78.get_pdf_banner(user_id)
    pdf_lock_on = await DARKXSIDE78.get_pdf_lock_mode(user_id)
    pdf_lock_password = await DARKXSIDE78.get_pdf_lock_password(user_id)
    pdf_banner_placement = await DARKXSIDE78.get_pdf_banner_placement(user_id) or "first"

    banner_status = "✓ Oɴ" if pdf_banner_on else "✘ Oғғ"
    lock_status = "✓ Oɴ" if pdf_lock_on else "✘ Oғғ"
    banner_file_status = "✓ Sᴇᴛ" if pdf_banner_file else "✘ Nᴏᴛ Sᴇᴛ"
    lock_pw_status = f"✓ Sᴇᴛ" if pdf_lock_password else "✘ Nᴏᴛ Sᴇᴛ"
    placement_status = {
        "first": "Fɪʀsᴛ Pᴀɢᴇ",
        "last": "Lᴀsᴛ Pᴀɢᴇ",
        "both": "Bᴏᴛʜ"
    }.get(pdf_banner_placement, "Fɪʀsᴛ Pᴀɢᴇ")

    text = (
        f"**PDF Mᴏᴅᴇ Sᴇᴛᴛɪɴɢs**\n\n**PDF Bᴀɴɴᴇʀ:**** {banner_status}**\n**Bᴀɴɴᴇʀ Fɪʟᴇ:**** {banner_file_status}**\n**PDF Lᴏᴄᴋ:**** {lock_status}**\n**Lᴏᴄᴋ Pᴀssᴡᴏʀᴅ:**** {lock_pw_status}**\n**Bᴀɴɴᴇʀ Pʟᴀᴄᴇᴍᴇɴᴛ:**** `{placement_status}`**\n\n**— Wʜᴇɴ PDF Bᴀɴɴᴇʀ ɪs ON, ʏᴏᴜʀ ʙᴀɴɴᴇʀ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴀᴅᴅᴇᴅ ᴛᴏ ᴀʟʟ ʀᴇɴᴀᴍᴇᴅ PDFs.**\n**— Wʜᴇɴ PDF Lᴏᴄᴋ ɪs ON, ᴀʟʟ ʀᴇɴᴀᴍᴇᴅ PDFs ᴡɪʟʟ ʙᴇ ʟᴏᴄᴋᴇᴅ ᴡɪᴛʜ ʏᴏᴜʀ ᴘᴀssᴡᴏʀᴅ.**\n**— Bᴀɴɴᴇʀ Pʟᴀᴄᴇᴍᴇɴᴛ ᴄᴏɴᴛʀᴏʟs ᴡʜᴇʀᴇ ʏᴏᴜʀ ʙᴀɴɴᴇʀ ɪs ᴀᴅᴅᴇᴅ (ғɪʀsᴛ, ʟᴀsᴛ, ᴏʀ ʙᴏᴛʜ ᴘᴀɢᴇs).**\n"
    )

    buttons = [
        [
            InlineKeyboardButton(
                f"PDF Bᴀɴɴᴇʀ: {'Dɪsᴀʙʟᴇ' if pdf_banner_on else 'Eɴᴀʙʟᴇ'}",
                callback_data=f"toggle_pdf_banner:{int(not pdf_banner_on)}"
            ),
            InlineKeyboardButton(
                f"PDF Lᴏᴄᴋ: {'Dɪsᴀʙʟᴇ' if pdf_lock_on else 'Eɴᴀʙʟᴇ'}",
                callback_data=f"toggle_pdf_lock:{int(not pdf_lock_on)}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Sᴇᴛ PDF Bᴀɴɴᴇʀ", callback_data="set_pdf_banner"
            ),
            InlineKeyboardButton(
                "Sᴇᴛ PDF Lᴏᴄᴋ Pᴀssᴡᴏʀᴅ", callback_data="set_pdf_lock_pw"
            ),
        ],
        [
            InlineKeyboardButton(
                f"Bᴀɴɴᴇʀ Pʟᴀᴄᴇᴍᴇɴᴛ: {placement_status}", callback_data=f"set_pdf_banner_place:{user_id}"
            ),
        ]
    ]

    if edit:
        if message.text != text or getattr(message.reply_markup, "inline_keyboard", None) != InlineKeyboardMarkup(buttons).inline_keyboard:
            await message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_callback_query(filters.regex(r"^set_pdf_banner_place:(\d+)$"))
async def set_pdf_banner_place_cb(client, callback_query):
    owner_id = int(callback_query.matches[0].group(1))
    if callback_query.from_user.id != owner_id:
        await callback_query.answer("Yᴏᴜ ᴄᴀɴ'ᴛ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs ғᴏʀ ᴀɴᴏᴛʜᴇʀ ᴜsᴇʀ!", show_alert=True)
        return
    buttons = [
        [
            InlineKeyboardButton("Fɪʀsᴛ Pᴀɢᴇ", callback_data=f"pdf_banner_place:first:{owner_id}"),
            InlineKeyboardButton("Lᴀsᴛ Pᴀɢᴇ", callback_data=f"pdf_banner_place:last:{owner_id}")
        ],
        [
            InlineKeyboardButton("Bᴏᴛʜ", callback_data=f"pdf_banner_place:both:{owner_id}")
        ]
    ]
    await callback_query.message.edit_text(
        "**Cʜᴏᴏsᴇ ᴅᴇғᴀᴜʟᴛ PDF ʙᴀɴɴᴇʀ ᴘʟᴀᴄᴇᴍᴇɴᴛ:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^pdf_banner_place:(first|last|both):(\d+)$"))
async def pdf_banner_place_choose_cb(client, callback_query):
    placement = callback_query.matches[0].group(1)
    owner_id = int(callback_query.matches[0].group(2))
    if callback_query.from_user.id != owner_id:
        await callback_query.answer("Yᴏᴜ ᴄᴀɴ'ᴛ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs ғᴏʀ ᴀɴᴏᴛʜᴇʀ ᴜsᴇʀ!", show_alert=True)
        return
    await DARKXSIDE78.set_pdf_banner_placement(owner_id, placement)
    await pdf_mode_settings(client, callback_query.message, edit=True, user_id=owner_id)
    await callback_query.answer(f"PDF ʙᴀɴɴᴇʀ ᴘʟᴀᴄᴇᴍᴇɴᴛ sᴇᴛ ᴛᴏ {placement}!", show_alert=True)

@Client.on_message(filters.command("set_pdf_banner_place"))
@check_ban_status
async def set_pdf_banner_place_cmd(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].strip().lower() not in ("first", "last", "both"):
        return await message.reply(
            "**Usᴀɢᴇ:** `/set_pdf_banner_place first|last|both`\n"
            "**Sᴇᴛ ᴡʜᴇʀᴇ ʏᴏᴜʀ PDF ʙᴀɴɴᴇʀ ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ʙʏ ᴅᴇғᴀᴜʟᴛ.**"
        )
    placement = args[1].strip().lower()
    await DARKXSIDE78.set_pdf_banner_placement(message.from_user.id, placement)
    await message.reply(f"**PDF ʙᴀɴɴᴇʀ ᴘʟᴀᴄᴇᴍᴇɴᴛ sᴇᴛ ᴛᴏ:** `{placement}`")

@Client.on_callback_query(filters.regex(r"^toggle_pdf_banner:(0|1)$"))
async def toggle_pdf_banner_cb(client, callback_query):
    mode = bool(int(callback_query.matches[0].group(1)))
    user_id = callback_query.from_user.id
    await DARKXSIDE78.set_pdf_banner_mode(user_id, mode)
    await pdf_mode_settings(client, callback_query.message, edit=True, user_id=user_id)
    await callback_query.answer(f"PDF Bᴀɴɴᴇʀ {'enabled' if mode else 'disabled'}.")

@Client.on_callback_query(filters.regex(r"^toggle_pdf_lock:(0|1)$"))
async def toggle_pdf_lock_cb(client, callback_query):
    mode = bool(int(callback_query.matches[0].group(1)))
    user_id = callback_query.from_user.id
    await DARKXSIDE78.set_pdf_lock_mode(user_id, mode)
    await pdf_mode_settings(client, callback_query.message, edit=True, user_id=user_id)
    await callback_query.answer(f"PDF Lᴏᴄᴋ {'enabled' if mode else 'disabled'}.")
    
@Client.on_callback_query(filters.regex(r"^set_pdf_banner$"))
async def set_pdf_banner_cb(client, callback_query):
    await callback_query.answer("Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ /set_pdf_banner ᴛᴏ sᴇᴛ ʏᴏᴜʀ ʙᴀɴɴᴇʀ.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^set_pdf_lock_pw$"))
async def set_pdf_lock_pw_cb(client, callback_query):
    await callback_query.answer("Sᴇɴᴅ /set_pdf_lock <password> ᴛᴏ sᴇᴛ ʏᴏᴜʀ PDF ʟᴏᴄᴋ ᴘᴀssᴡᴏʀᴅ.", show_alert=True)

