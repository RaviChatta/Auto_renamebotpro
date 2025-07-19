import re, os, time
from os import environ, getenv
id_pattern = re.compile(r'^.\d+$') 


class Config(object):
    API_ID    = os.environ.get("API_ID", "22817133")
    API_HASH  = os.environ.get("API_HASH", "65b44989de9accc59c64691b308da0f7")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7790118521:AAFA13wK8zI4jSJK-nOMowacyVoHTCKJMFg") 

    DB_NAME = os.environ.get("DB_NAME","Cluster0")     
    DB_URL  = os.environ.get("DB_URL","mongodb+srv://gd3251791:qAFhXxHXPkaNxw9u@cluster0.mr2u1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    PORT = os.environ.get("PORT", "8080")
 
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://files.catbox.moe/yly8lj.jpg")
    START_STICKER   = "CAACAgUAAxkBAAEM6M9oYj65EbUcQmXuCIf9KRhJFzj31AAC8w4AAmjvEFeX9xEJreldPB4E"
    FORCE_PIC   = os.environ.get("FORCE_PIC", "https://files.catbox.moe/3mtgb2.jpg")
    ADMINS       = [int(admins) if id_pattern.search(admins) else admins for admins in os.environ.get('ADMINS', '1047253913').split()]
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '1047253913').split()]
    FORCE_SUB_CHANNELS = os.environ.get('FORCE_SUB_CHANNELS', ' ').split(', ')
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "@emledhurrror")
    DUMP_CHANNEL = os.environ.get("DUMP_CHANNEL", "-1002308381248")
    DUMP = False
    BOT_CHANNEL_NAME = os.environ.get("BOT_CHANNEL_NAME", "TFIBOTS")
    BOT_CHANNEL_USERNAME = os.environ.get("BOT_CHANNEL_USERNAME", "Autorenamer2bot")
    SUPPORT_CHANNEL_NAME = os.environ.get("SUPPORT_CHANNEL_NAME", "TFIBOTS_SUPPORT ")
    UPDATE_CHANNEL = os.environ.get("SUPPORT_CHANNEL_USERNAME", "TFIBOTS ")
    SUPPORT_CHANNEL_USERNAME = os.environ.get("SUPPORT_CHANNEL_USERNAME", "TFIBOTS_SUPPORT ")
    SUPPORT_GROUP = os.environ.get("SUPPORT_CHANNEL_USERNAME", "TFIBOTS_SUPPORT ")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "Autorenamer2bot")
    BOT_NAME = os.environ.get("BOT_NAME", "Ai Hoshino")
    OWNER_NAME = os.environ.get("OWNER_NAME", "Raaaaavi")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "Raaaaavi")
    DEVELOPER_USERNAME = os.environ.get("DEVELOPER_USERNAME", "Raaaaavi")
    DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Raaaaavi")
    TOKEN_API = "de5bd3536a538fb73d70f5d82c5a55820a869b0a"
    SHORTENER_URL = "https://pocolinks.com"
    PREMIUM_USERS_PER_PAGE = 15
    TOKEN_ID_LENGTH = 8
    SHORTENER_TOKEN_GEN = 100
    REFER_TOKEN = 100
    #DEEPAI_API_KEY = "e5056491-3a9f-4685-8021-4851b5986073"
    #REPLICATE_API_TOKEN = "r8_Im5t1ANUr3xurbRnBzuFreMtzccdOl43tjBuL"
    UPI_ID = "test@paytm"
    VERSION = "4.1.2"
    LAST_UPDATED = "2025-05-01"
    DB_VERSION = "1.4.2"
    FLOODWAIT_RETRIES = 999
    FLOODWAIT_WAIT = 30
    DEFAULT_TOKEN = 100
    UPDATE_TIME = 7
    PAUSE_AFTER_COMPLETE = 1.2
    LEADERBOARD_DELETE_TIMER = 30
    RENAMED_DELETE_TIMER = 120
    ADMIN_OR_PREMIUM_TASK_LIMIT = 5
    NORMAL_TASK_LIMIT = 3
    ADMIN_USAGE_MODE = False
    GLOBAL_TOKEN_MODE = True
    GLOBAL_TOKEN_EXPIRY = None
    SESSION_NAME = "Renamer"
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))
    WEBHOOK_PORT = os.environ.get("WEBHOOK_PORT", "8000")

    #Auto approve 
    CHAT_ID = [int(app_chat_id) if id_pattern.search(app_chat_id) else app_chat_id for app_chat_id in environ.get('CHAT_ID', '0').split()]
    TEXT = environ.get("APPROVED_WELCOME_TEXT", "<b>{mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {title} ɪs ᴀᴘᴘʀᴏᴠᴇᴅ.\n\‣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @codflix_bots</b>")
    APPROVED = environ.get("APPROVED_WELCOME", "on").lower()
    
class Txt(object):
        
    START_TXT = """<b>ʜᴇʏ! 

» ɪ ᴀᴍ ᴀᴅᴠᴀɴᴄᴇᴅ ʀᴇɴᴀᴍᴇ ʙᴏᴛ! ᴡʜɪᴄʜ ᴄᴀɴ ᴀᴜᴛᴏʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ғɪʟᴇs ᴡɪᴛʜ ᴄᴜsᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ ᴀɴᴅ ᴛʜᴜᴍʙɴᴀɪʟ ᴀɴᴅ ᴀʟsᴏ sᴇǫᴜᴇɴᴄᴇ ᴛʜᴇᴍ ᴘᴇʀғᴇᴄᴛʟʏ</b>"""
    
    FILE_NAME_TXT = """<b>» <u>Setup Auto-Rename Format</u></b>

<b>Available Variables:</b>
➲ <code>{season}</code> – Season number  
➲ <code>{episode}</code> – Episode number  
➲ <code>{title}</code> – Main title  
➲ <code>{year}</code> – Year (for movies)  
➲ <code>{resolution}</code> – Video resolution  
➲ <code>{audio}</code> – Audio language or format  
➲ <code>{codec}</code> – Video codec  
➲ <code>{chapter}</code> – Chapter (if any)

<b>Formats:</b>  
➲ <b>TV Series:</b> <code>[S{{season}} - E{{episode}}] {{title}} [{{resolution}}] [{{audio}}]</code>  
➲ <b>Movies:</b> <code>{{title}} ({{year}}) [{{resolution}}] [{{audio}}] [{{codec}}]</code>

<b>Auto-Rename Toggle:</b>  
➲ <code>/autorename_on</code> – Enable auto-renaming  
➲ <code>/autorename_off</code> – Disable auto-renaming

<b>Usage:</b>  
Use the above variables in your rename format with the <code>/autorename</code> command.  
The bot will extract values from the filename and apply them automatically.
<b>⚠️ Disclaimer:</b>  
Title and season extraction may vary depending on filename format.  
Please test with a few files first to ensure proper results.
"""



    ABOUT_TXT = f"""<b>❍ ᴍʏ ɴᴀᴍᴇ : <a href="https://t.me/{Config.BOT_USERNAME}">{Config.BOT_NAME}</a>
❍ ᴅᴇᴠᴇʟᴏᴩᴇʀ : <a href="https://t.me/{Config.DEVELOPER_USERNAME}">{Config.DEVELOPER_NAME}</a>
❍ ᴏᴡɴᴇʀ : <a href="https://t.me/{Config.OWNER_USERNAME}">{Config.OWNER_NAME}</a>
❍ ʟᴀɴɢᴜᴀɢᴇ : <a href="https://www.python.org/">ᴘʏᴛʜᴏɴ</a>
❍ ᴅᴀᴛᴀʙᴀꜱᴇ : <a href="https://www.mongodb.com/">ᴍᴏɴɢᴏ ᴅʙ</a>
❍ ʜᴏꜱᴛᴇᴅ ᴏɴ : <a href="https://t.me/{Config.DEVELOPER_USERNAME}">ᴠᴘs</a>
❍ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ : <a href="https://t.me/{Config.BOT_CHANNEL_USERNAME}">{Config.BOT_CHANNEL_NAME}</a>
❍ ʜᴇʟᴘ ᴄʜᴀɴɴᴇʟ : <a href="https://t.me/{Config.SUPPORT_CHANNEL_USERNAME}">{Config.SUPPORT_CHANNEL_NAME}</a>

➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ ᴍᴇ.</b>"""

    
    THUMBNAIL_TXT = """<b><u>» ᴛᴏ ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ</u></b>
    
➲ </code>/set_thumb</code>: ꜱᴇɴᴅ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ꜱᴇᴛ ɪᴛ ᴀꜱ ᴀ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/del_thumb</code>: ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴏʟᴅ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/view_thumb</code>: ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/get_thumb</code>: ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ᴛʜᴜᴍʙɴᴀɪʟ ғʀᴏᴍ ᴏᴛʜᴇʀ ᴠɪᴅᴇᴏs ᴏʀ ᴅᴏᴄ.

ɴᴏᴛᴇ: ɪꜰ ɴᴏ ᴛʜᴜᴍʙɴᴀɪʟ ꜱᴀᴠᴇᴅ ɪɴ ʙᴏᴛ ᴛʜᴇɴ, ɪᴛ ᴡɪʟʟ ᴜꜱᴇ ᴛʜᴜᴍʙɴᴀɪʟ ᴏꜰ ᴛʜᴇ ᴏʀɪɢɪɴɪᴀʟ ꜰɪʟᴇ ᴛᴏ ꜱᴇᴛ ɪɴ ʀᴇɴᴀᴍᴇᴅ ꜰɪʟᴇ"""

    CAPTION_TXT = """<b><u>» ᴛᴏ ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ ᴀɴᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ</u></b>
    
<b>ᴠᴀʀɪᴀʙʟᴇꜱ :</b>         
ꜱɪᴢᴇ: {filesize}
ᴅᴜʀᴀᴛɪᴏɴ: {duration}
ꜰɪʟᴇɴᴀᴍᴇ: {filename}

➲ </code>/set_caption</code>: ᴛᴏ ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ </code>/see_caption</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ </code>/del_caption</code>: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.

» ꜰᴏʀ ᴇx:- /set_caption ꜰɪʟᴇ ɴᴀᴍᴇ: {filesize}"""

    PROGRESS_BAR = """
<b>» Sɪᴢᴇ</b> : {1} | {2}
<b>» Dᴏɴᴇ</b> : {0}%
<b>» Sᴘᴇᴇᴅ</b> : {3}/s
<b>» ETA</b> : {4} """
    
    
    DONATE_TXT = f"""<blockquote> ᴛʜᴀɴᴋs ғᴏʀ sʜᴏᴡɪɴɢ ɪɴᴛᴇʀᴇsᴛ ɪɴ ᴅᴏɴᴀᴛɪᴏɴ</blockquote>

<b><i>💞  ɪꜰ ʏᴏᴜ ʟɪᴋᴇ ᴏᴜʀ ʙᴏᴛ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ᴅᴏɴᴀᴛᴇ ᴀɴʏ ᴀᴍᴏᴜɴᴛ ₹𝟷𝟶, ₹𝟸𝟶, ₹𝟻𝟶, ₹𝟷𝟶𝟶, ᴇᴛᴄ.</i></b>

ᴅᴏɴᴀᴛɪᴏɴs ᴀʀᴇ ʀᴇᴀʟʟʏ ᴀᴘᴘʀᴇᴄɪᴀᴛᴇᴅ ɪᴛ ʜᴇʟᴘs ɪɴ ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ

 <u>ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴅᴏɴᴀᴛᴇ ᴛʜʀᴏᴜɢʜ ᴜᴘɪ</u>

 ᴜᴘɪ ɪᴅ : <code>{Config.UPI_ID}</code>

ɪғ ʏᴏᴜ ᴡɪsʜ ʏᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴜs ss
ᴏɴ - @{Config.OWNER_USERNAME}"""

    PREMIUM_TXT = """<b>ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇ ᴀɴᴅ ᴇɴJᴏʏ ᴇxᴄʟᴜsɪᴠᴇ ғᴇᴀᴛᴜʀᴇs:
○ ᴜɴʟɪᴍɪᴛᴇᴅ Rᴇɴᴀᴍɪɴɢ.
○ ɴᴏ ᴀᴅꜱ.
○ ᴇᴀʀʟʏ Aᴄᴄᴇss.
○ ᴍᴏʀᴇ ᴘʀɪᴏʀɪᴛʏ

• ᴜꜱᴇ /plan ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴏᴜʀ ᴘʟᴀɴꜱ ᴀᴛ ᴏɴᴄᴇ.

➲ ғɪʀsᴛ sᴛᴇᴘ : ᴘᴀʏ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴘʟᴀɴ ᴛᴏ ᴛʜᴇ ᴜᴘɪ ɪᴅ ᴏʀ Qʀ.
➲ secoɴᴅ sᴛᴇᴘ : ᴛᴀᴋᴇ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ ᴀɴᴅ sʜᴀʀᴇ ɪᴛ ᴅɪʀᴇᴄᴛʟʏ ʜᴇʀᴇ: @Raaaaavi
➲ ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ sᴛᴇᴘ : ᴏʀ ᴜᴘʟᴏᴀᴅ ᴛʜᴇ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴇʀᴇ ᴀɴᴅ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ /bought ᴄᴏᴍᴍᴀɴᴅ. [ᴍᴀʏ ɴᴏᴛ ᴡᴏʀᴋ ᴘʀᴏᴘᴇʀʟʏ]

Yᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴡɪʟʟ ʙᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴀғᴛᴇʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ</b>"""

    PREPLANS_TXT = """<b>👋 ʜᴇʟʟᴏ ʙʀᴏ,
    
🎖️ <u>ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs</u> :

Pʀɪᴄɪɴɢ:
➜ ᴅᴀɪʟʏ ᴘʀᴇᴍɪᴜᴍ: ₹10/ᴅᴀʏ
➜ ᴍᴏɴᴛʜʟʏ ᴘʀᴇᴍɪᴜᴍ: ₹80/ᴍᴏɴᴛʜ
➜ ʟɪꜰᴇᴛɪᴍᴇ ᴘʀᴇᴍɪᴜᴍ: ₹459
➜ ғᴏʀ ʙᴏᴛ ʜᴏsᴛɪɴɢ: [ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ](https://t.me/{Config.DEVELOPER_USERNAME})

➲ ᴜᴘɪ ɪᴅ - <code>{Config.UPI_ID}</code>

‼️ᴜᴘʟᴏᴀᴅ ᴛʜᴇ ᴘᴀʏᴍᴇɴᴛ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴇʀᴇ ᴀɴᴅ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ /bought ᴄᴏᴍᴍᴀɴᴅ.</b>"""
    
    HELP_TXT = """
    ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ
    """

    ALL_TXT = """<b>ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴄᴏᴍᴍᴀɴᴅꜱ:

ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs🫧

ʀᴇɴᴀᴍᴇ ʙᴏᴛ ɪꜱ ᴀ ʜᴀɴᴅʏ ᴛᴏᴏʟ ᴛʜᴀᴛ ʜᴇʟᴘꜱ ʏᴏᴜ ʀᴇɴᴀᴍᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.

➲ /autorename: ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ʏᴏᴜʀ ꜰɪʟᴇꜱ.
➲ /ssequence: sᴛᴀʀᴛ sᴇǫᴜᴇɴᴄᴇ.
➲ /esequence: ᴇɴᴅ sᴇǫᴜᴇɴᴄᴇ.
➲ /refer: ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇғᴇʀ ʟɪɴᴋ ᴀɴᴅ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʀᴇғᴇʀ ᴄᴏᴜɴᴛ.
➲ /gentoken: ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴏᴋᴇɴ ʟɪɴᴋ.
➲ /bal: ᴛᴏ ᴄʜᴇᴄᴋ ʀᴇᴍᴀɪɴɪɴɢ ᴛᴏᴋᴇɴs.
➲ /setsource: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ sᴏᴜʀᴄᴇ ғᴏʀ ʀᴇɴᴀᴍɪɴɢ ғɪʟᴇs.
➲ /pdfmode: ᴛᴏ sᴇᴇ ᴀʟʟ ᴘᴅғ ʀᴇʟᴀᴛᴇᴅ sᴇᴛᴛɪɴɢs.
➲ /pdf_replace: ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴘᴅғ ᴘᴀɢᴇs ᴡɪᴛʜ ʏᴏᴜʀ ʙᴀɴɴᴇʀ.
➲ /pdf_extractor: ᴛᴏ ᴇxᴛʀᴀᴄᴛ ғɪʀsᴛ ᴀɴᴅ ʟᴀsᴛ ᴘᴀɢᴇs ᴏғ ᴘᴅғ.
➲ /pdf_add: ᴛᴏ ᴀᴅᴅ ʏᴏᴜʀ ʙᴀɴɴᴇʀ ɪɴ ᴘᴅғ.
➲ /pdf_remove: ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘᴀɢᴇs ғʀᴏᴍ ᴘᴅғ.
➲ /set_pdf_lock: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘᴅғ ʟᴏᴄk (ᴅᴇғᴀᴜʟᴛ).
➲ /pdf_lock:ᴛᴏ ʟᴏᴄᴋ ᴘᴅғ ᴡɪᴛʜ ᴘᴀssᴡᴏʀᴅ sᴇᴛ ʙʏ ʏᴏᴜ ᴏʀ ᴀɴʏ ᴘᴀssᴡᴏʀᴅ ᴇ.ɢ. /ᴘᴅғ_ʟᴏᴄᴋ <ᴘᴀssᴡᴏʀᴅ>.
➲ /upscale_ffmpeg: ᴛᴏ ᴜᴘsᴄᴀʟᴇ ʏᴏᴜʀ ɪᴍɢ ᴜsɪɴɢ ғғᴍᴘᴇɢ.
➲ /admin_mode: ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴏғғ ᴀᴅᴍɪɴ ᴍᴏᴅᴇ.
➲ /add_admin: ᴛᴏ ᴀᴅᴅ ᴀɴ ᴀᴅᴍɪɴ (ᴛᴇᴍᴘ).
➲ /queue: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇɴᴀᴍɪɴɢ ǫᴜᴇᴜᴇ.
➲ /cancel: ᴛᴏ ᴄᴀɴᴄᴇʟ ʏᴏᴜʀ ʀᴇɴᴀᴍɪɴɢ ᴊᴏʙ.
➲ /renamed: ᴛᴏ ᴠɪᴇᴡ ʀᴇɴᴀᴍᴇᴅ sᴛᴀᴛs.
➲ /info: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ʙᴏᴛ ɪɴғᴏ.
➲ /rename_history: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇɴᴀᴍɪɴɢ ʜɪsᴛᴏʀʏ.
➲ /setmedia: ᴛᴏ sᴇᴛ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ ɪɴ ʏᴏᴜʀ ʙᴏᴛ.
➲ /token_usage: ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴏғғ ᴛᴏᴋᴇɴ ᴜsᴀɢᴇ.
➲ /set_caption: ᴛᴏ ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ /view_caption: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ.
➲ /del_caption: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ.
➲ /setthumb: ᴛᴏ sᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ /getthumb: ᴛᴏ ɢᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ ғʀᴏᴍ ᴏᴛʜᴇʀ ᴠɪᴅᴇᴏs.
➲ /viewthumb: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ /delthumb: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ /setbanner: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ /viewbanner: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ /delbanner: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ /metadata: ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴏғғ ᴍᴇᴛᴀᴅᴀᴛᴀ.
➲ /help: ɢᴇᴛ ǫᴜɪᴄᴋ ᴀꜱꜱɪꜱᴛᴀɴᴄᴇ.</b>"""

    SEND_METADATA = """
<b>--Mᴇᴛᴀᴅᴀᴛᴀ Sᴇᴛᴛɪɴɢs:--</b>

➜ /metadata: Tᴜʀɴ ᴏɴ ᴏʀ ᴏғғ ᴍᴇᴛᴀᴅᴀᴛᴀ.

<b>Description</b> : Mᴇᴛᴀᴅᴀᴛᴀ ᴡɪʟʟ ᴄʜᴀɴɢᴇ MKV ᴠɪᴅᴇᴏ ғɪʟᴇs ɪɴᴄʟᴜᴅɪɴɢ ᴀʟʟ ᴀᴜᴅɪᴏ, sᴛʀᴇᴀᴍs, ᴀɴᴅ sᴜʙᴛɪᴛʟᴇ ᴛɪᴛʟᴇs."""


    SOURCE_TXT = """f
<b>ʜᴇʏ,
ᴛʜɪs ɪs ᴀɴ ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ʙᴏᴛ,
ᴄʀᴇᴀᴛᴇᴅ ʙʏ [{Config.BOT_CHANNEL_NAME}](https://t.me/{Config.BOT_CHANNEL_USERNAME}).</b>

<b>ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ :
[ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)
[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)
ᴀɴᴅ ᴜsɪɴɢ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.</b> """

    META_TXT = """
**ᴍᴀɴᴀɢɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ ғᴏʀ ʏᴏᴜʀ ᴠɪᴅᴇᴏs ᴀɴᴅ ғɪʟᴇs**

**ᴠᴀʀɪᴏᴜꜱ ᴍᴇᴛᴀᴅᴀᴛᴀ:**

- **ᴛɪᴛʟᴇ**: Descriptive title of the media.
- **ᴀᴜᴛʜᴏʀ**: The creator or owner of the media.
- **ᴀʀᴛɪꜱᴛ**: The artist associated with the media.
- **ᴀᴜᴅɪᴏ**: Title or description of audio content.
- **ꜱᴜʙᴛɪᴛʟᴇ**: Title of subtitle content.
- **ᴠɪᴅᴇᴏ**: Title or description of video content.
- **ᴇɴᴄᴏᴅᴇ ʙʏ**: The person who encoded the video.
- **ᴄᴜꜱᴛᴏᴍ ᴛᴀɢ**: Any Title.
- **ᴄᴏᴍᴍᴇɴᴛ**: Any Title.
 

**ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴏғғ ᴍᴇᴛᴀᴅᴀᴛᴀ:**
➜ </code>/metadata</code>: Turn on or off metadata.

**ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ꜱᴇᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:**

➜ </code>/settitle</code>: Set a custom title of media.
➜ </code>/setauthor</code>: Set the author.
➜ </code>/setartist</code>: Set the artist.
➜ </code>/setaudio</code>: Set audio title.
➜ </code>/setsubtitle</code>: Set subtitle title.
➜ </code>/setvideo</code>: Set video title.
➜ </code>/setencoded_by</code>: Set encoded by title.
➜ </code>/setcustom_tag</code>: Set custom tag title.
➜ </code>/setcomment</code>: Set comment title.

**ᴇxᴀᴍᴘʟᴇ:** </code>/settitle</code> Your Title Here

**ᴜꜱᴇ ᴛʜᴇꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴇɴʀɪᴄʜ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ᴡɪᴛʜ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴍᴇᴛᴀᴅᴀᴛᴀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ!**
"""
    PDF_TXT = """
➲ </code>/pdfmode</code>: ᴛᴏ sᴇᴇ ᴀʟʟ ᴘᴅғ ʀᴇʟᴀᴛᴇᴅ sᴇᴛᴛɪɴɢs.
➲ </code>/pdf_replace</code>: ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ᴘᴅғ ᴘᴀɢᴇs ᴡɪᴛʜ ʏᴏᴜʀ ʙᴀɴɴᴇʀ.
➲ </code>/pdf_extractor</code>: ᴛᴏ ᴇxᴛʀᴀᴄᴛ ғɪʀsᴛ ᴀɴᴅ ʟᴀsᴛ ᴘᴀɢᴇs ᴏғ ᴘᴅғ.
➲ </code>/pdf_add</code>: ᴛᴏ ᴀᴅᴅ ʏᴏᴜʀ ʙᴀɴɴᴇʀ ɪɴ ᴘᴅғ.
➲ </code>/pdf_remove</code>: ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴘᴀɢᴇs ғʀᴏᴍ ᴘᴅғ.
➲ </code>/set_pdf_lock</code>: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘᴅғ ʟᴏᴄk (ᴅᴇғᴀᴜʟᴛ).
➲ </code>/pdf_lock</code>:ᴛᴏ ʟᴏᴄᴋ ᴘᴅғ ᴡɪᴛʜ ᴘᴀssᴡᴏʀᴅ sᴇᴛ ʙʏ ʏᴏᴜ ᴏʀ ᴀɴʏ ᴘᴀssᴡᴏʀᴅ ᴇ.ɢ. /ᴘᴅғ_ʟᴏᴄᴋ <ᴘᴀssᴡᴏʀᴅ>.
➲ </code>/setbanner</code>: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ </code>/viewbanner</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ </code>/delbanner</code>: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.

"""
    TELEGRAPH_TXT = """<b>ʜᴇʟᴘ: ᴛᴇʟᴇɢʀᴀᴘʜ ᴅᴏ ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ᴡɪᴛʜ ᴛᴇʟᴇɢʀᴀ.ᴘʜ ᴍᴏᴅᴜʟᴇ! 
  
 ᴜꜱᴀɢᴇ:</code> /telegraph </code>- ꜱᴇɴᴅ ᴍᴇ ᴘɪᴄᴛᴜʀᴇ ᴏʀ ᴠɪᴅᴇᴏ ᴜɴᴅᴇʀ (5ᴍʙ) 
  
 ɴᴏᴛᴇ: 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ɢᴏᴜᴘꜱ ᴀɴᴅ ᴘᴍꜱ 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴇᴠᴇʀʏᴏɴᴇ</b>"""

    TOKEN_TXT = """
    ʜᴇʟᴘ: ᴛᴇʟᴇɢʀᴀᴘʜ ᴅᴏ ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ᴡɪᴛʜ ᴛᴇʟᴇɢʀᴀ.ᴘʜ ᴍᴏᴅᴜʟᴇ! 

➲ </code>/token</code>: ᴄʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ᴛᴏᴋᴇɴs ʏᴏᴜ ʜᴀᴠᴇ
➲ </code>/gentoken</code>: ᴛᴏ generate ad token to get rename tokens
➲ </code>/refer</code>: refer to get free tokens.
  
 ɴᴏᴛᴇ: 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ɢᴏᴜᴘꜱ ᴀɴᴅ ᴘᴍꜱ 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴇᴠᴇʀʏᴏɴᴇ
 """
    ANIME_TXT = """
Get information about animes!

USAGE:
➢ </code>/anime</code> [name] - Get detailed information about a specific anime.
➢ </code>/findanime</code> - Reply to an anime image to identify the anime from the scene.
➢ </code>/sauce</code> - Reply to an image to find its source (anime, manga, or artwork).
"""
    SORT_TXT = """
➲ <code>/autorename_on</code> - ᴇɴᴀʙʟᴇ ᴀᴜᴛᴏ ʀᴇɴᴀᴍɪɴɢ  
➲ </code>/ssequence</code>: sᴛᴀʀᴛ sᴇǫᴜᴇɴᴄᴇ.
➲ </code>/esequence</code>: ᴇɴᴅ sᴇǫᴜᴇɴᴄᴇ.

"""

    UPSCALE_TXT = """
ʜᴇʟᴘ: ᴜᴘꜱᴄᴀʟᴇ ɪᴍᴀɢᴇꜱ ᴜꜱɪɴɢ ᴀɪ ᴘᴏᴡᴇʀ!

➲ </code>/upscale_ffmpeg</code>: ꜱᴇɴᴅ ᴀɴ ɪᴍᴀɢᴇ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴜᴘꜱᴄᴀʟᴇ ɪᴛ


ɴᴏᴛᴇ:
ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ᴡᴏʀᴋꜱ ɪɴ ʙᴏᴛʜ ɢʀᴏᴜᴘꜱ ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ
ᴇᴠᴇʀʏᴏɴᴇ ᴄᴀɴ ᴜꜱᴇ ɪᴛ ʀᴇɢᴀʀᴅʟᴇꜱꜱ ᴏꜰ ʀᴏʟᴇ

"""

    FONT_TXT = """
ᴜꜱᴀɢᴇ 
  
 ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴍᴏᴅᴜʟᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ꜰᴏɴᴛ ꜱᴛyʟᴇ   
  
 ᴄᴏᴍᴍᴀɴᴅ : </code>/font</code> ʏᴏᴜʀ ᴛᴇxᴛ (ᴏᴩᴛɪᴏɴᴀʟ) 
 ᴇɢ:- /font ʜᴇʟʟᴏ

"""
    TOOLS_TXT = """
📚 ʜᴇʀᴇ ᴀʀᴇ ᴍʏ ᴄᴏᴍᴍᴀɴᴅꜱ ʟɪꜱᴛ ꜰᴏʀ ᴀʟʟ ʙᴏᴛ Users ⇊

➲ </code>/refer</code>: ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇғᴇʀ ʟɪɴᴋ ᴀɴᴅ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʀᴇғᴇʀ ᴄᴏᴜɴᴛ.
➲ </code>/renamed</code>: ᴛᴏ ᴠɪᴇᴡ ʀᴇɴᴀᴍᴇᴅ sᴛᴀᴛs.
➲ </code>/rename_history</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇɴᴀᴍɪɴɢ ʜɪsᴛᴏʀʏ.
➲ </code>/setmedia</code>: ᴛᴏ sᴇᴛ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ ɪɴ ʏᴏᴜʀ ʙᴏᴛ.
➲ </code>/set_caption</code>: ᴛᴏ ꜱᴇᴛ ᴀ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴ.
➲ </code>\set_source</code>: ᴛᴏ ꜱᴇᴛ ᴀ ʀᴇɴᴀᴍᴇ ꜱᴏᴜʀᴄᴇ
➲ </code>/view_caption</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ.
➲ </code>/del_caption</code>: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ.
➲ </code>/setthumb</code>: ᴛᴏ sᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/getthumb</code>: ᴛᴏ ɢᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ ғʀᴏᴍ ᴏᴛʜᴇʀ ᴠɪᴅᴇᴏs.
➲ </code>/viewthumb</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/delthumb</code>: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜᴜᴍʙɴᴀɪʟ.
➲ </code>/setbanner</code>: ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ </code>/viewbanner</code>: ᴛᴏ ᴠɪᴇᴡ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ </code>/delbanner</code>: ᴛᴏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴅғ ʙᴀɴɴᴇʀ.
➲ </code>/metadata</code>: ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴏғғ ᴍᴇᴛᴀᴅᴀᴛᴀ.
➲ </code>/help</code>: ɢᴇᴛ ǫᴜɪᴄᴋ ᴀꜱꜱɪꜱᴛᴀɴᴄᴇ.
"""
    ADMIN_TXT = """
📚 Here are my commands list for Admins ⇊

➲ </code>/token_usage</code>: ᴛᴏ ᴛᴜʀɴ ᴏɴ/ᴏꜰꜰ ᴛᴏᴋᴇɴ ᴜꜱᴀɢᴇ.
➲ </code>/info</code>: sʏꜱᴛᴇᴍ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ.
➲ </code>/add_premium</code>: ᴀᴅᴅ ᴀɴʏ ᴜꜱᴇʀ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ.
➲ </code>/remove_premium</code>: ʀᴇᴍᴏᴠᴇ ᴀɴʏ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴘʀᴇᴍɪᴜᴍ.
➲ </code>/premium_users</code>: ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ.
➲ </code>/ban</code>: ʙᴀɴ ᴀ ᴜꜱᴇʀ [ᴀᴅᴍɪɴ ᴏɴʟʏ].
➲ </code>/unban</code>: ᴛᴏ ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ [ᴀᴅᴍɪɴ ᴏɴʟʏ].
➲ </code>/broadcast</code>: ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.
➲ </code>/admin_mode</code>: ᴛᴏɢɢʟᴇ ᴀᴅᴍɪɴ ᴍᴏᴅᴇ ᴏɴ/ᴏꜰꜰ.
➲ </code>/add_admin</code>: ᴀᴅᴅ ᴀ sᴜᴅᴏ ᴜꜱᴇʀ.
➲ </code>/status</code>: ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛᴜꜱ.
➲ </code>/users</code>: ᴄʜᴇᴄᴋ ᴀʟʟ ʙᴏᴛ ᴜꜱᴇʀꜱ.
➲ </code>/add_token</code>: ᴀᴅᴅ ᴛᴏᴋᴇɴ ᴛᴏ ᴀ ᴜꜱᴇʀ.
➲ </code>/restart</code>: ʀᴇꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.
"""

    STICKER_TXT = """ <b> 

›› </code>/stickerid</code> : ᴛᴏ ɢᴇᴛ ꜱᴛɪᴄᴋᴇʀ 
                         
</b>"""
