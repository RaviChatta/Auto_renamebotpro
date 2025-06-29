from pyrogram import Client, filters 
from helper.database import DARKXSIDE78
from pyrogram.types import Message
import os
from functools import wraps
from PIL import Image
import aiohttp
from io import BytesIO
import aiofiles
from config import Config

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

#@Client.on_message(filters.command("free_upscale") & filters.reply)
#@check_ban_status
#async def free_upscale_photo(client, message):
    #replied = message.reply_to_message
    #if not replied or not replied.photo:
     #   return await message.reply("**Reply to a photo with /free_upscale to upscale it for free!**")

  #  status = await message.reply("**Upscaling for free... Please wait.**")
   # photo_path = await replied.download()

  #  api_url = "https://api.deepai.org/api/torch-srgan"
   # headers = {"api-key": Config.DEEPAI_API_KEY}
   # upscaled_bytes = None

  #  try:
     #   async with aiohttp.ClientSession() as session:
  #          with open(photo_path, "rb") as f:
      #          data = aiohttp.FormData()
      #          data.add_field('image', f, filename="image.jpg", content_type='image/jpeg')
      #          async with session.post(api_url, data=data, headers=headers) as resp:
      #              result = await resp.json()
      #              upscaled_url = result.get("output_url")
      #              if not upscaled_url:
      #                  error_msg = result.get("err") or result.get("status") or str(result)
      #                  await status.edit(f"**Upscaling failed:** {error_msg}")
      #                  return

      #      async with session.get(upscaled_url) as resp:
      #          upscaled_bytes = await resp.read()

      #  await client.send_photo(message.chat.id, upscaled_bytes, caption="**Upscaled image (DeepAI Free)**")
      #  await status.delete()
   # except Exception as e:
     #   await status.edit(f"**Upscaling failed:** `{e}`")
   # finally:
   #     if os.path.exists(photo_path):
   #         os.remove(photo_path)

@Client.on_message(filters.private & filters.command(['get_thumb', 'getthumb']) & filters.reply)
@check_ban_status
async def get_file_thumb(client, message: Message):
    if not message.reply_to_message or not (message.reply_to_message.document or message.reply_to_message.video):
        return await message.reply_text("**Pʟᴇᴀsᴇ Rᴇᴘʟʏ ᴛᴏ ᴀ Dᴏᴄᴜᴍᴇɴᴛ ᴏʀ Vɪᴅᴇᴏ ᴛʜᴀᴛ ʜᴀs ᴀ Tʜᴜᴍʙɴᴀɪʟ.**")

    media = message.reply_to_message.document or message.reply_to_message.video

    thumb = (
        media.thumbs[0] if getattr(media, "thumbs", None)
        else media.thumbnail if getattr(media, "thumbnail", None)
        else None
    )

    if not thumb:
        return await message.reply_text("**Nᴏ Tʜᴜᴍʙɴᴀɪʟ Fᴏᴜɴᴅ ɪɴ ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.**")

    status_msg = await message.reply_text("**Fᴇᴛᴄʜɪɴɢ Tʜᴜᴍʙɴᴀɪʟ... Pʟᴇᴀsᴇ Wᴀɪᴛ.**")

    try:
        downloaded_thumb = await client.download_media(thumb)
        await client.send_photo(chat_id=message.chat.id, photo=downloaded_thumb, caption="**Hᴇʀᴇ ɪs ᴛʜᴇ Tʜᴜᴍʙɴᴀɪʟ.**")
        os.remove(downloaded_thumb)
    except Exception as e:
        await message.reply_text(f"**Eʀʀᴏʀ:** `{e}`")
    finally:
        await status_msg.delete()

@Client.on_message(filters.private & filters.command('set_caption'))
@check_ban_status
async def add_caption(client, message):
    if len(message.command) == 1:
       return await message.reply_text("**Gɪᴠᴇ Cᴀᴘᴛɪᴏɴ\n\nExᴀᴍᴘʟᴇ: `/set_caption Nᴀᴍᴇ ➠ : {filename} \n\nSɪᴢᴇ ➠ : {filesize} \n\nDᴜʀᴀᴛɪᴏɴ ➠ : {duration}`**")
    caption = message.text.split(" ", 1)[1]
    await DARKXSIDE78.set_caption(message.from_user.id, caption=caption)
    await message.reply_text("**Yᴏᴜʀ Cᴀᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ Sᴜᴄᴄᴇssғᴜʟʟʏ Sᴇᴛ...**")

@Client.on_message(filters.private & filters.command('del_caption'))
@check_ban_status
async def delete_caption(client, message):
    caption = await madflixbotz.get_caption(message.from_user.id)  
    if not caption:
       return await message.reply_text("**Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Cᴀᴘᴛɪᴏɴ.**")
    await DARKXSIDE78.set_caption(message.from_user.id, caption=None)
    await message.reply_text("**Yᴏᴜʀ Cᴀᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ...**")

@Client.on_message(filters.private & filters.command(['see_caption', 'view_caption']))
@check_ban_status
async def see_caption(client, message):
    caption = await DARKXSIDE78.get_caption(message.from_user.id)  
    if caption:
       await message.reply_text(f"**Cᴜʀʀᴇɴᴛ Cᴀᴘᴛɪᴏɴ:**\n\n`{caption}`")
    else:
       await message.reply_text("**Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Cᴀᴘᴛɪᴏɴ.**")


@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
@check_ban_status
async def viewthumb(client, message):    
    thumb = await DARKXSIDE78.get_thumbnail(message.from_user.id)
    if thumb:
       await client.send_photo(chat_id=message.chat.id, photo=thumb)
    else:
        await message.reply_text("**Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Tʜᴜᴍʙɴᴀɪʟ.**") 

@Client.on_message(filters.private & filters.command(['del_thumb', 'delthumb']))
@check_ban_status
async def removethumb(client, message):
    await DARKXSIDE78.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Yᴏᴜʀ Tʜᴜᴍʙɴᴀɪʟ ʜᴀs ʙᴇᴇɴ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ.**")

@Client.on_message(filters.private & filters.command(['set_thumb', 'setthumb', 'set_thumbnail', 'setthumbnail']) & filters.reply)
@check_ban_status
async def set_thumb_cmd(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.photo:
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ `/set_thumb` ᴛᴏ sᴇᴛ ɪᴛ ᴀs ʏᴏᴜʀ ᴛʜᴜᴍʙɴᴀɪʟ.**")
    mkn = await message.reply_text("Pʟᴇᴀsᴇ Wᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ...")
    await DARKXSIDE78.set_thumbnail(message.from_user.id, file_id=replied.photo.file_id)
    await mkn.edit("**Tʜᴜᴍʙɴᴀɪʟ ʜᴀs ʙᴇᴇɴ Sᴀᴠᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ.**")

@Client.on_message(filters.private & filters.command(['set_pdf_banner', 'set_banner', 'setbanner']) & filters.reply)
@check_ban_status
async def set_pdf_banner(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.photo:
        return await message.reply("**Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ `/set_pdf_banner` ᴛᴏ sᴇᴛ ʏᴏᴜʀ PDF ʙᴀɴɴᴇʀ.**")
    mkn = await message.reply_text("Pʟᴇᴀsᴇ Wᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ...")
    await DARKXSIDE78.set_pdf_banner(message.from_user.id, replied.photo.file_id)
    await mkn.edit("**PDF ʙᴀɴɴᴇʀ ʜᴀs ʙᴇᴇɴ Sᴀᴠᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ.**")

@Client.on_message(filters.private & filters.command(['view_pdf_banner', 'view_banner', 'viewbanner']))
@check_ban_status
async def view_pdf_banner(client, message: Message):
    user_id = message.from_user.id
    banner_file_id = await DARKXSIDE78.get_pdf_banner(user_id)
    if banner_file_id:
        await client.send_photo(chat_id=message.chat.id, photo=banner_file_id, caption="**Hᴇʀᴇ ɪs ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ PDF ʙᴀɴɴᴇʀ.**")
    else:
        await message.reply_text("**Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴇᴛ ᴀ PDF ʙᴀɴɴᴇʀ ʏᴇᴛ.**")

@Client.on_message(filters.private & filters.command(['delete_banner', 'deletebanner', 'delbanner', 'del_banner', 'delete_pdf_banner']))
@check_ban_status
async def delete_pdf_banner(client, message: Message):
    user_id = message.from_user.id
    banner_file_id = await DARKXSIDE78.get_pdf_banner(user_id)
    if banner_file_id:
        await DARKXSIDE78.set_pdf_banner(user_id, None)
        await message.reply_text("**Yᴏᴜʀ PDF ʙᴀɴɴᴇʀ ʜᴀs ʙᴇᴇɴ Sᴜᴄᴄᴇssғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ.**")
    else:
        await message.reply_text("**Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ PDF ʙᴀɴɴᴇʀ.**")
