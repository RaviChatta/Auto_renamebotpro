import aiohttp, asyncio, warnings, pytz
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server
import pyrogram.utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
from animebot import AnimeBot  # Import the AnimeBot class
#from plugins.compress import start_compressor, compressor 

pyrogram.utils.MIN_CHANNEL_ID = -1002258136705

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=Config.SESSION_NAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=8,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.start_time = time.time()
        self.anime_bot = None  # Will be initialized in start()
      #  self.compressor = compressor  # Store compressor instance

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME  
        
        # Initialize AnimeBot
        self.anime_bot = AnimeBot(self)
        await self.anime_bot.initialize()
        
        # Start the anime queue processor
        asyncio.create_task(self.anime_bot.adaptive_queue_processor())
      #  asyncio.create_task(start_compressor(self))  # Start compressor
       

      #  app.add_handler(start_compressor)
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", Config.WEBHOOK_PORT).start()     
        print(f"{me.first_name} Is Started.....✨️")

        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))

        for chat_id in [Config.LOG_CHANNEL, Config.SUPPORT_CHANNEL_USERNAME]:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time_str = curr.strftime('%I:%M:%S %p')
                
                await self.send_photo(
                    chat_id=chat_id,
                    photo=Config.START_PIC,
                    caption=(
                        f"**{Config.BOT_NAME} ɪs ʀᴇsᴛᴀʀᴛᴇᴅ ᴀɢᴀɪɴ  !**\n\n"
                        f"ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​: `{uptime_string}`\n"
                        f"✨ <b>New Feature:</b> Anime detection commands added!"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=f"https://t.me/{Config.BOT_CHANNEL_USERNAME}")
                        ]]
                    )
                )

            except Exception as e:
                print(f"Failed to send message in chat {chat_id}: {e}")

    async def stop(self, *args):
        # Cleanup AnimeBot resources
        if self.anime_bot:
            await self.anime_bot.shutdown()
         #   await cleanup_compressor()
        await super().stop()

if __name__ == "__main__":
    bot = Bot()
    bot.run()
