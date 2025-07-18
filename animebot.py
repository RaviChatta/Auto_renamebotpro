import asyncio
import psutil
from collections import deque
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatAction
from typing import Dict, Optional, List, Union
import logging
import aiohttp
import os
import tempfile
from datetime import timedelta, datetime
import json
from calendar import month_name
from io import BytesIO

logger = logging.getLogger(__name__)

class AnimeBot:
    def __init__(self, bot: Client):
        self.bot = bot
        self.session = None
        self.temp_files = set()
        
        # Configuration
        self.cpu_threshold = 80
        self.max_queue_size = 20
        self.request_timeout = 30
        
        # Queues
        self.request_queue = deque(maxlen=self.max_queue_size)
        self.active_tasks = set()
        
        # APIs
        self.trace_moe_key = os.getenv("TRACE_MOE_KEY")
        self.saucenao_key = os.getenv("SAUCENAO_API_KEY")
        self.anilist_api = "https://graphql.anilist.co"
        
        # Constants
        self.ANIME_QUERY = """
        query ($id: Int, $idMal: Int, $search: String) {
          Media(id: $id, idMal: $idMal, type: ANIME, search: $search) {
            id
            idMal
            title {
              romaji
              english
              native
            }
            type
            format
            status(version: 2)
            description(asHtml: true)
            startDate {
              year
              month
              day
            }
            endDate {
              year
              month
              day
            }
            season
            seasonYear
            episodes
            duration
            chapters
            volumes
            countryOfOrigin
            source
            hashtag
            trailer {
              id
              site
              thumbnail
            }
            updatedAt
            coverImage {
              extraLarge
              large
            }
            bannerImage
            genres
            synonyms
            averageScore
            meanScore
            popularity
            trending
            favourites
            tags {
              name
              description
              rank
            }
            relations {
              edges {
                node {
                  id
                  title {
                    romaji
                    english
                    native
                  }
                  format
                  status
                  source
                  averageScore
                  siteUrl
                }
                relationType
              }
            }
            characters {
              edges {
                role
                node {
                  name {
                    full
                    native
                  }
                  siteUrl
                }
              }
            }
            studios {
              nodes {
                 name
                 siteUrl
              }
            }
            isAdult
            nextAiringEpisode {
              airingAt
              timeUntilAiring
              episode
            }
            airingSchedule {
              edges {
                node {
                  airingAt
                  timeUntilAiring
                  episode
                }
              }
            }
            externalLinks {
              url
              site
            }
            rankings {
              rank
              year
              context
            }
            reviews {
              nodes {
                summary
                rating
                score
                siteUrl
                user {
                  name
                }
              }
            }
            siteUrl
          }
        }
        """

    async def initialize(self):
        """Initialize the anime bot"""
        self.session = aiohttp.ClientSession()
        self.register_handlers()
        asyncio.create_task(self.adaptive_queue_processor())
        logger.info("AnimeBot initialized")

    async def shutdown(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            await self.cleanup_temp_files()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

    async def cleanup_temp_files(self):
        """Cleanup temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Couldn't delete temp file {file_path}: {e}")
        self.temp_files.clear()

    def get_system_load(self) -> float:
        """Get current system CPU load"""
        return psutil.cpu_percent(interval=1)

    async def adaptive_queue_processor(self):
        """Process requests based on system load"""
        while True:
            try:
                if self.request_queue and self.get_system_load() < self.cpu_threshold:
                    task = self.request_queue.popleft()
                    if task['message_id'] not in self.active_tasks:
                        self.active_tasks.add(task['message_id'])
                        asyncio.create_task(self.process_request(task))
                
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(5)

    # ======================
    # Core Functionality
    # ======================

    async def process_request(self, task: Dict):
        """Process an anime request"""
        try:
            message = await self.bot.get_messages(task['chat_id'], task['message_id'])
            if not message:
                return

            # Cleanup queued message if exists
            if 'queued_message_id' in task:
                try:
                    await self.bot.delete_messages(task['chat_id'], task['queued_message_id'])
                except Exception:
                    pass

            if task['type'] == 'findanime':
                await self.handle_findanime(message)
            elif task['type'] == 'sauce':
                await self.handle_sauce(message)
            elif task['type'] == 'anime':
                await self.handle_anime_search(message)
                
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            try:
                await message.reply_text("⚠️ An error occurred while processing your request")
            except Exception:
                pass
        finally:
            self.active_tasks.discard(task['message_id'])

    async def handle_findanime(self, message: Message):
        """Handle /findanime command"""
        if not message.reply_to_message or not (
            message.reply_to_message.photo or 
            (message.reply_to_message.document and 
             message.reply_to_message.document.mime_type.startswith('image/'))
        ):
            await message.reply_text("🔍 Please reply to an anime screenshot with /findanime")
            return

        await self.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        try:
            file_id = (message.reply_to_message.photo.file_id if message.reply_to_message.photo 
                      else message.reply_to_message.document.file_id)
            image_bytes = await self.download_image(file_id)
            if not image_bytes:
                raise ValueError("Failed to download image")

            trace_data = await self.trace_moe_search(image_bytes)
            if not trace_data or not trace_data.get('result'):
                await message.reply_text("❌ Couldn't identify the anime. Try a clearer image.")
                return

            best_match = trace_data['result'][0]
            anilist_data = await self.fetch_anilist(best_match['anilist'])

            # Format response
            from_time = best_match.get('from', 0)
            timestamp = f"{int(from_time // 60):02}:{int(from_time % 60):02}"
            
            response = {
                'title': anilist_data.get('title', {}),
                'episode': best_match.get('episode', 'N/A'),
                'episodes': anilist_data.get('episodes', 0),
                'timestamp': timestamp,
                'confidence': float(best_match.get('similarity', 0)) * 100,
                'anilist_url': anilist_data.get('siteUrl', '#'),
                'video_url': f"{best_match.get('video', '')}&size=l" if best_match.get('video') else None,
                'cover_image': anilist_data.get('coverImage', {}).get('large', None),
            }

            caption = self._format_findanime_response(response)
            await self.send_anime_result(message, response, caption)

        except Exception as e:
            logger.error(f"Findanime error: {e}")
            await message.reply_text("❌ Failed to process your request. Please try again.")

    async def handle_sauce(self, message: Message):
        """Handle /sauce command"""
        if not message.reply_to_message or not (
            message.reply_to_message.photo or 
            (message.reply_to_message.document and 
             message.reply_to_message.document.mime_type.startswith('image/'))
        ):
            await message.reply_text("🔍 Please reply to an image with /sauce")
            return

        await self.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        try:
            file_id = (message.reply_to_message.photo.file_id if message.reply_to_message.photo 
                      else message.reply_to_message.document.file_id)
            image_bytes = await self.download_image(file_id)
            if not image_bytes:
                raise ValueError("Failed to download image")

            # Try SauceNAO first
            sauce_data = await self.saucenao_search(image_bytes)
            if sauce_data and sauce_data.get('results'):
                best_result = sauce_data['results'][0]
                data = best_result.get('data', {})
                
                response = {
                    'source': data.get('title') or data.get('source', 'Unknown'),
                    'similarity': float(best_result.get('header', {}).get('similarity', 0)),
                    'url': data.get('ext_urls', ['#'])[0] if data.get('ext_urls') else '#',
                    'author': data.get('author') or data.get('creator') or 'Unknown',
                }
            else:
                # Fallback to trace.moe
                trace_data = await self.trace_moe_search(image_bytes)
                if not trace_data or not trace_data.get('result'):
                    await message.reply_text("❌ Couldn't find the source. Try a clearer image.")
                    return

                best_match = trace_data['result'][0]
                anilist_data = await self.fetch_anilist(best_match['anilist'])

                response = {
                    'source': anilist_data.get('title', {}).get('english') or 
                             anilist_data.get('title', {}).get('romaji', 'Unknown'),
                    'similarity': float(best_match.get('similarity', 0)) * 100,
                    'url': anilist_data.get('siteUrl', '#'),
                    'author': "Unknown",
                }

            caption = self._format_sauce_response(response)
            await message.reply_text(
                caption, 
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            
            # Mention user in groups
            if message.chat.type in ["group", "supergroup"]:
                await message.reply_text(
                    f"👆 For {message.from_user.mention}",
                    parse_mode=ParseMode.HTML
                )

        except Exception as e:
            logger.error(f"Sauce error: {e}")
            await message.reply_text("❌ Failed to process your request. Please try again.")

    async def handle_anime_search(self, message: Message):
        """Handle /anime command with premium design"""
        try:
            search_query = message.text.split(" ", 1)
            if len(search_query) < 2:
                await message.reply_text("🎌 <b>Please provide an anime title to search.</b>\n\nExample: <code>/anime Attack on Titan</code>")
                return
            
            search_query = search_query[1].strip()
            variables = {"search": search_query}
            
            # Fetch anime data
            anime_data = await self.search_anilist(variables)
            if not anime_data:
                await message.reply_text("❌ <b>No anime found with that title.</b>")
                return
            
            # Format all the data
            title_romaji = anime_data['title'].get('romaji', 'N/A')
            title_english = anime_data['title'].get('english', title_romaji)
            title_native = anime_data['title'].get('native', title_romaji)
            
            description = self.format_description(anime_data.get('description'))
            score = anime_data.get('averageScore', 0)
            episodes = anime_data.get('episodes', 'N/A')
            status = anime_data.get('status', 'N/A').replace('_', ' ').title()
            duration = f"{anime_data.get('duration', 0)} mins" if anime_data.get('duration') else "N/A"
            start_date = self.format_date(anime_data.get('startDate'))
            end_date = self.format_date(anime_data.get('endDate'))
            
            genres = ", ".join(anime_data.get('genres', [])) if anime_data.get('genres') else "N/A"
            studios = ", ".join([s['name'] for s in anime_data['studios']['nodes']]) if anime_data.get('studios') else "N/A"
            
            # Check if anime is NSFW
            is_adult = "🔞 <b>Adult Content:</b> <code>Yes</code>\n" if anime_data.get('isAdult') else ""
            
            # Format trailer button if available
            trailer = anime_data.get('trailer', {})
            trailer_btn = []
            if trailer and trailer.get('site') == "youtube":
                trailer_url = f"https://youtu.be/{trailer['id']}"
                trailer_btn = [InlineKeyboardButton("🎬 Watch Trailer", url=trailer_url)]
            
            # Create keyboard
            buttons = []
            if trailer_btn:
                buttons.append(trailer_btn)
            buttons.append([InlineKeyboardButton("📖 View on AniList", url=anime_data['siteUrl'])])
            
            # Get cover image (prefer extraLarge, fallback to large)
            cover_image = anime_data['coverImage'].get('extraLarge') or anime_data['coverImage'].get('large')
            
            # Format the final message
            caption = f"""
🎌 <b>{title_english}</b> | <i>{title_native}</i>

⭐ <b>Rating:</b> <code>{score}</code> {self.create_progress_bar(score)}
📺 <b>Episodes:</b> <code>{episodes}</code>
⏳ <b>Duration:</b> <code>{duration}</code>
🗓️ <b>Aired:</b> <code>{start_date} to {end_date}</code>
📌 <b>Status:</b> <code>{status}</code>
{is_adult}
🎭 <b>Genres:</b> <code>{genres}</code>
🏢 <b>Studios:</b> <code>{studios}</code>

📝 <b>Description:</b>
{description}
"""
            # Send the result
            try:
                if cover_image:
                    await message.reply_photo(
                        photo=cover_image,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await message.reply_text(
                        text=caption,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                logger.error(f"Failed to send anime result: {e}")
                await message.reply_text(
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            
        except Exception as e:
            logger.exception("Error in anime command:")
            error_msg = await message.reply_text(
                "⚠️ <b>An error occurred while processing your request.</b>\n"
                "Please try again later or check the anime title.",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(10)
            await error_msg.delete()

    # ======================
    # API Methods
    # ======================

    async def trace_moe_search(self, image_data: bytes) -> Optional[Dict]:
        """Search for anime using trace.moe API"""
        headers = {'x-trace-key': self.trace_moe_key} if self.trace_moe_key else {}
        
        async with self.session.post(
            "https://api.trace.moe/search",
            data={'image': image_data},
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            logger.error(f"trace.moe failed: HTTP {resp.status}")
            return None

    async def saucenao_search(self, image_data: bytes) -> Optional[Dict]:
        """Search for source using SauceNAO API"""
        if not self.saucenao_key:
            return None
            
        form_data = aiohttp.FormData()
        form_data.add_field('db', '999')
        form_data.add_field('output_type', '2')
        form_data.add_field('api_key', self.saucenao_key)
        form_data.add_field('file', image_data, filename='image.jpg')
        
        async with self.session.post(
            "https://saucenao.com/search.php",
            data=form_data,
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            logger.error(f"SauceNAO failed: HTTP {resp.status}")
            return None

    async def fetch_anilist(self, anilist_id: int) -> Dict:
        """Fetch anime metadata from AniList"""
        query = """query($id: Int) {
            Media(id: $id, type: ANIME) {
                id
                title { romaji english native }
                description(asHtml: false)
                episodes
                duration
                status
                startDate { year month day }
                endDate { year month day }
                season
                seasonYear
                coverImage { large extraLarge }
                bannerImage
                genres
                averageScore
                siteUrl
                studios(isMain: true) { nodes { name } }
                isAdult
                trailer { id site }
            }
        }"""
        
        async with self.session.post(
            self.anilist_api,
            json={'query': query, 'variables': {'id': anilist_id}},
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('data', {}).get('Media', {})
            logger.error(f"AniList failed: HTTP {resp.status}")
            return {}

    async def search_anilist(self, variables: Dict) -> Optional[Dict]:
        """Search anime on AniList"""
        async with self.session.post(
            self.anilist_api,
            json={'query': self.ANIME_QUERY, 'variables': variables},
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('data', {}).get('Media', None)
            logger.error(f"AniList search failed: HTTP {resp.status}")
            return None

    # ======================
    # Utility Methods
    # ======================

    async def download_image(self, file_id: str) -> Optional[bytes]:
        """Download image to memory"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_path = temp_file.name
                self.temp_files.add(temp_path)
                
                await self.bot.download_media(file_id, file_name=temp_path)
                
                with open(temp_path, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return None

    async def send_anime_result(self, message: Message, data: Dict, caption: str):
        """Send anime result with appropriate media"""
        try:
            if data.get('video_url'):
                sent_msg = await message.reply_video(
                    data['video_url'],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            elif data.get('cover_image'):
                sent_msg = await message.reply_photo(
                    data['cover_image'],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            else:
                sent_msg = await message.reply_text(
                    caption,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            
            # Mention user in groups
            if message.chat.type in ["group", "supergroup"]:
                await sent_msg.reply_text(
                    f"👆 For {message.from_user.mention}",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Failed to send media: {e}")
            await message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

    def format_description(self, description: str, max_length: int = 500) -> str:
        """Format anime description with proper cleaning"""
        if not description:
            return ""
        
        # Clean HTML tags
        description = description.replace("<br>", "\n").replace("<i>", "").replace("</i>", "")
        
        # Shorten if needed
        if len(description) > max_length:
            description = f"{description[:max_length]}..."
        
        return description.strip()

    def format_date(self, date_dict: Dict) -> str:
        """Format date from AniList response"""
        if not date_dict:
            return "Unknown"
        try:
            return f"{date_dict.get('day', '?')}/{date_dict.get('month', '?')}/{date_dict.get('year', '?')}"
        except:
            return "Unknown"

    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar"""
        filled = '█' * int(percentage/100 * length)
        empty = '░' * (length - len(filled))
        return f"{filled}{empty} {percentage:.1f}%"

    # ======================
    # Formatting Methods
    # ======================

    def _format_findanime_response(self, data: Dict) -> str:
        """Format anime detection result"""
        title = data.get('title', {}).get('english') or data.get('title', {}).get('romaji', 'Unknown')
        episode = data.get('episode', 'N/A')
        total_eps = data.get('episodes', '1')
        confidence = data.get('confidence', 0)
        timestamp = data.get('timestamp', '00:00 – 00:00')
        url = data.get('anilist_url', '#')
        
        is_movie = str(total_eps) == "1"
        movie_tag = "🎞️ <b>Type:</b> <code>Movie</code>\n" if is_movie else ""
    
        return (
            "╭━━《 <b>ANIME RESULT</b> 》━━╮\n\n"
            f"📖 <b>Title:</b> <code>{title}</code>\n"
            f"{movie_tag}"
            f"🎬 <b>Episodes:</b> « {episode} / {total_eps} »\n"
            f"🎯 <b>Match Confidence:</b> <code>{confidence:.2f}%</code>\n"
            f"⏰ <b>TimeStamp:</b> <code>{timestamp}</code>\n\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯\n"
            f"<a href='{url}'>🔗 <b>[ MORE INFO ]</b></a>"
        )

    def _format_sauce_response(self, data: Dict) -> str:
        """Format source detection result"""
        return (
            "╭━━《 <b>SOURCE RESULT</b> 》━━╮\n\n"
            f"📖 <b>Source:</b> <code>{data.get('source', 'Unknown')}</code>\n"
            f"👤 <b>Author:</b> <code>{data.get('author', 'Unknown')}</code>\n"
            f"🎯 <b>Similarity:</b> <code>{data.get('similarity', 0):.2f}%</code>\n\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯\n"
            f"<a href='{data.get('url', '#')}'>🔗 <b>[ VIEW SOURCE ]</b></a>"
        )

    def _format_anime_info(self, data: Dict) -> str:
        """Format anime information"""
        title_eng = data.get('title', {}).get('english', 'N/A')
        title_romaji = data.get('title', {}).get('romaji', 'N/A')
        title_native = data.get('title', {}).get('native', 'N/A')
        
        titles = []
        if title_eng and title_eng != title_romaji:
            titles.append(f"<b>English:</b> {title_eng}")
        if title_romaji:
            titles.append(f"<b>Romaji:</b> {title_romaji}")
        if title_native and title_native != title_romaji:
            titles.append(f"<b>Native:</b> {title_native}")
        
        title_text = "\n".join(titles) if titles else "N/A"

        start_date = data.get('startDate', {})
        end_date = data.get('endDate', {})
        start_date_str = f"{start_date.get('year', '?')}-{start_date.get('month', '?')}-{start_date.get('day', '?')}"
        end_date_str = f"{end_date.get('year', '?')}-{end_date.get('month', '?')}-{end_date.get('day', '?')}"
        
        duration = data.get('duration', 0)
        duration_str = str(timedelta(minutes=duration)) if duration else "N/A"
        
        studios = [studio['name'] for studio in data.get('studios', {}).get('nodes', [])]
        studios_str = ", ".join(studios) if studios else "Unknown"
        
        genres_str = ", ".join(data.get('genres', [])) if data.get('genres') else "N/A"
        
        return (
            f"╭━━《 <b>ANIME INFO</b> 》━━╮\n\n"
            f"{title_text}\n\n"
            f"📊 <b>Status:</b> {data.get('status', 'N/A')}\n"
            f"🎬 <b>Episodes:</b> {data.get('episodes', 'N/A')}\n"
            f"⏳ <b>Duration:</b> {duration_str}\n"
            f"⭐ <b>Score:</b> {data.get('averageScore', 'N/A')}\n"
            f"🗓️ <b>Aired:</b> {start_date_str} to {end_date_str}\n"
            f"🌱 <b>Season:</b> {data.get('season', 'N/A')} {data.get('seasonYear', '')}\n"
            f"🏢 <b>Studios:</b> {studios_str}\n"
            f"🏷️ <b>Genres:</b> {genres_str}\n\n"
            f"📝 <b>Description:</b>\n{data.get('description', 'No description available.')[:500]}"
            f"{'...' if len(data.get('description', '')) > 500 else ''}\n\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n"
            f"<a href='{data.get('siteUrl', '#')}'>🔗 <b>[ VIEW ON ANILIST ]</b></a>"
        )

    # ======================
    # Handler Registration
    # ======================

    def register_handlers(self):
        """Register all command handlers and callbacks"""

        @self.bot.on_message(filters.command("findanime") & (filters.private | filters.group))
        async def findanime_handler(client: Client, message: Message):
            if not message.reply_to_message or not (
                message.reply_to_message.photo or 
                (message.reply_to_message.document and 
                 message.reply_to_message.document.mime_type.startswith('image/'))
            ):
                await message.reply_text("🔍 Reply to an anime screenshot with /findanime")
                return

            if len(self.request_queue) >= self.max_queue_size:
                await message.reply_text("🚧 Queue is full. Please try again later.")
                return

            queued_msg = await message.reply_text("🔄 Your request has been queued...")
            
            self.request_queue.append({
                'type': 'findanime',
                'message_id': message.id,
                'chat_id': message.chat.id,
                'reply_to': message.reply_to_message.id,
                'queued_message_id': queued_msg.id
            })

        @self.bot.on_message(filters.command("sauce") & (filters.private | filters.group))
        async def sauce_handler(client: Client, message: Message):
            if not message.reply_to_message or not (
                message.reply_to_message.photo or 
                (message.reply_to_message.document and 
                 message.reply_to_message.document.mime_type.startswith('image/'))
            ):
                await message.reply_text("🔍 Reply to an image with /sauce")
                return

            if len(self.request_queue) >= self.max_queue_size:
                await message.reply_text("🚧 Queue is full. Please try again later.")
                return

            queued_msg = await message.reply_text("🔄 Your request has been queued...")
            
            self.request_queue.append({
                'type': 'sauce',
                'message_id': message.id,
                'chat_id': message.chat.id,
                'reply_to': message.reply_to_message.id,
                'queued_message_id': queued_msg.id
            })

        @self.bot.on_message(filters.command("anime") & (filters.private | filters.group))
        async def anime_handler(client: Client, message: Message):
            if len(self.request_queue) >= self.max_queue_size:
                await message.reply_text("🚧 Queue is full. Please try again later.")
                return

            queued_msg = await message.reply_text("🔍 Searching for anime...")
            
            self.request_queue.append({
                'type': 'anime',
                'message_id': message.id,
                'chat_id': message.chat.id,
                'queued_message_id': queued_msg.id
            })

        @self.bot.on_callback_query(filters.regex("^anime_detail_"))
        async def anime_detail_callback(client: Client, callback_query):
            try:
                parts = callback_query.data.split('_')
                if len(parts) != 4:
                    await callback_query.answer("Invalid request")
                    return

                anime_id = int(parts[2])
                requester_id = int(parts[3])

                if callback_query.from_user.id != requester_id:
                    await callback_query.answer("This menu isn't for you!", show_alert=True)
                    return

                await callback_query.answer("Fetching details...")
                anime_data = await self.fetch_anilist(anime_id)
                
                if not anime_data:
                    await callback_query.message.edit_text("❌ Failed to fetch details.")
                    return

                caption = self._format_anime_info(anime_data)
                cover_image = anime_data.get('coverImage', {}).get('extraLarge') or anime_data.get('coverImage', {}).get('large')

                try:
                    if cover_image:
                        await callback_query.message.reply_photo(
                            cover_image,
                            caption=caption,
                            parse_mode=ParseMode.HTML
                        )
                        await callback_query.message.delete()
                    else:
                        await callback_query.message.edit_text(
                            caption,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True
                        )
                except Exception:
                    await callback_query.message.edit_text(
                        caption,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                logger.error(f"Callback error: {e}")
                await callback_query.answer("An error occurred")
