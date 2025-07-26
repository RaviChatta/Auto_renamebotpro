import motor.motor_asyncio
import datetime
import pytz
from config import Config
import logging

class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self._client.server_info()
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise e
        self.DARKXSIDE78 = self._client[database_name]
        self.col = self.DARKXSIDE78.user
        self.rename_logs = self.DARKXSIDE78.rename_logs
        self.token_links = self.DARKXSIDE78.token_links
        self.global_settings = self.DARKXSIDE78.global_settings
        
    def new_user(self, id):
        return dict(
            _id=int(id),
            join_date=datetime.datetime.now(pytz.utc).date().isoformat(),
            file_id=None,
            caption=None,
            metadata=True,
            metadata_code="Telegram : @DARKXSIDE78",
            format_template=None,
            rename_count=0,
            first_name="",
            username="",
            token_tasks=[],
            is_premium=False,
            premium_expiry=None,
            token=Config.DEFAULT_TOKEN,
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                ban_reason=''
            )
        )

    async def is_premium(self, user_id: int):
        """Check if a user is a premium user."""
        try:
            user = await self.col.find_one({"_id": user_id})
            return user.get("is_premium", False) if user else False
        except Exception as e:
            logging.error(f"Error checking premium status for user {user_id}: {e}")
            return False

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            user["first_name"] = u.first_name or "Unknown"
            user["username"] = u.username or ""
            try:
                await self.col.insert_one(user)
                logging.info(f"User {u.id} added to database")
            except Exception as e:
                logging.error(f"Error adding user {u.id} to database: {e}")

    async def is_user_exist(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return bool(user)
        except Exception as e:
            logging.error(f"Error checking if user {id} exists: {e}")
            return False

    async def total_users_count(self):
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logging.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        try:
            all_users = self.col.find({})
            return all_users
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return None

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({"_id": int(user_id)})
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def set_thumbnail(self, id, file_id):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {"file_id": file_id}})
        except Exception as e:
            logging.error(f"Error setting thumbnail for user {id}: {e}")

    async def get_thumbnail(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("file_id", None) if user else None
        except Exception as e:
            logging.error(f"Error getting thumbnail for user {id}: {e}")
            return None

    async def set_caption(self, id, caption):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {"caption": caption}})
        except Exception as e:
            logging.error(f"Error setting caption for user {id}: {e}")

    async def get_caption(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("caption", None) if user else None
        except Exception as e:
            logging.error(f"Error getting caption for user {id}: {e}")
            return None

    async def set_format_template(self, id, format_template):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"format_template": format_template}}
            )
        except Exception as e:
            logging.error(f"Error setting format template for user {id}: {e}")

    async def get_format_template(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("format_template", None) if user else None
        except Exception as e:
            logging.error(f"Error getting format template for user {id}: {e}")
            return None

    async def is_user_banned(self, user_id: int):
        """Check if a user is banned and return the ban status and reason."""
        try:
            user = await self.col.find_one({"_id": user_id})
            if not user:
                return False, None
            ban_status = user.get("ban_status", {})
            return ban_status.get("is_banned", False), ban_status.get("ban_reason", "No reason provided")
        except Exception as e:
            logging.error(f"Error checking ban status for user {user_id}: {e}")
            return False, None

    async def add_rename_history(self, user_id: int, original_name: str, renamed_name: str):
        """Add a renamed file to the user's history."""
        await self.rename_logs.update_one(
            {"_id": user_id},
            {"$push": {"history": {"original_name": original_name, "renamed_name": renamed_name}}},
            upsert=True
        )

    async def get_rename_history(self, user_id: int):
        """Retrieve the rename history for a user."""
        user_data = await self.rename_logs.find_one({"_id": user_id})
        return user_data.get("history", []) if user_data else []

    async def create_token_link(self, user_id: int, token_id: str, tokens: int):
        expiry = datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=24)
        try:
            await self.token_links.update_one(
                {"_id": token_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "tokens": tokens,
                        "used": False,
                        "expiry": expiry
                    }
                },
                upsert=True
            )
            logging.info(f"Token link created for user {user_id} with token ID {token_id}.")
        except Exception as e:
            logging.error(f"Error creating token link: {e}")

    async def get_token_link(self, token_id: str):
        try:
            token_data = await self.token_links.find_one({"_id": token_id})
            return token_data
        except Exception as e:
            logging.error(f"Error fetching token link for token ID {token_id}: {e}")
            return None

    async def mark_token_used(self, token_id: str):
        try:
            await self.token_links.update_one(
                {"_id": token_id},
                {"$set": {"used": True}}
            )
            logging.info(f"Token {token_id} marked as used.")
        except Exception as e:
            logging.error(f"Error marking token as used: {e}")

    async def set_token(self, user_id, token):
        try:
            await self.col.update_one(
                {"_id": int(user_id)},
                {"$set": {"token": token}}
            )
            logging.info(f"Token updated for user {user_id}.")
        except Exception as e:
            logging.error(f"Error setting token for user {user_id}: {e}")

    async def get_token(self, user_id):
        try:
            user = await self.col.find_one({"_id": int(user_id)})
            return user.get("token", Config.DEFAULT_TOKEN) if user else Config.DEFAULT_TOKEN
        except Exception as e:
            logging.error(f"Error getting token for user {user_id}: {e}")
            return Config.DEFAULT_TOKEN

    async def set_media_preference(self, id, media_type):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"media_type": media_type}}
            )
        except Exception as e:
            logging.error(f"Error setting media preference for user {id}: {e}")

    async def get_media_preference(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("media_type", None) if user else None
        except Exception as e:
            logging.error(f"Error getting media preference for user {id}: {e}")
            return None
# In helper/database.py

    async def set_autorename_status(self, user_id: int, status: bool):
        await self.col.update_one(
            {"_id": user_id},
            {"$set": {"autorename_enabled": status}},
            upsert=True
        )

    async def get_autorename_status(self, user_id: int) -> bool:
        user = await self.col.find_one({"_id": user_id})
        return user.get("autorename_enabled", False) if user else False

    async def set_metadata_source(self, user_id: int, source: str):
        await self.col.update_one(
            {"_id": user_id},
            {"$set": {"metadata_source": source}},
            upsert=True
        )

    async def get_metadata_source(self, user_id: int) -> str:
        user_data = await self.col.find_one({"_id": user_id})
        return user_data.get("metadata_source", "filename") if user_data else "filename"

    async def get_metadata(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('metadata', "Off")

    async def set_metadata(self, user_id, metadata):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'metadata': metadata}})

    async def get_title(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('title', '@TFIBOTS')

    async def set_title(self, user_id, title):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'title': title}})

    async def get_author(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('author', '[@TFIBOTS]')

    async def set_author(self, user_id, author):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'author': author}})

    async def get_artist(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('artist', '[@TFIBOTS]')

    async def set_artist(self, user_id, artist):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'artist': artist}})

    async def get_audio(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('audio', '[@TFIBOTS]')

    async def set_audio(self, user_id, audio):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'audio': audio}})

    async def get_subtitle(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('subtitle', "[@TFIBOTS]")

    async def set_subtitle(self, user_id, subtitle):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'subtitle': subtitle}})

    async def get_video(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('video', '[@TFIBOTS]')

    async def set_video(self, user_id, video):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'video': video}})

    async def get_encoded_by(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('encoded_by', "@TFIBOTS [RAVI]")

    async def set_encoded_by(self, user_id, encoded_by):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'encoded_by': encoded_by}})
        
    async def get_custom_tag(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('custom_tag', "[@TFIBOTS]")

    async def set_custom_tag(self, user_id, custom_tag):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'custom_tag': custom_tag}})

    async def get_commentz(self, user_id):
        user = await self.col.find_one({'_id': int(user_id)})
        return user.get('commentz', "[@TFIBOTS]")

    async def set_commentz(self, user_id, commentz):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'commentz': custom_tag}})

    async def set_pdf_lock_password(self, user_id, password):
        await self.col.update_one({"_id": user_id}, {"$set": {"pdf_lock_password": password}}, upsert=True)

    async def get_pdf_lock_password(self, user_id):
        user = await self.col.find_one({"_id": user_id})
        return user.get("pdf_lock_password") if user else None

    async def set_pdf_banner(self, user_id, file_id):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"pdf_banner": file_id}}, upsert=True)

    async def get_pdf_banner(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("pdf_banner") if user else None

    async def set_metadata_source(self, user_id, source):
        await self.col.update_one({"_id": int(user_id)}, {"$set": {"metadata_source": source}}, upsert=True)

    async def get_metadata_source(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("metadata_source", "filename") if user else "filename"
    
    async def set_pdf_banner_placement(self, user_id, placement):
        """
        Set the user's default PDF banner placement ('first', 'last', or 'both').
        """
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"pdf_banner_placement": placement}},
            upsert=True
        )

    async def get_pdf_banner_placement(self, user_id):
        """
        Get the user's default PDF banner placement.
        Returns 'first' if not set.
        """
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("pdf_banner_placement", "first") if user else "first"

    async def set_pdf_banner_mode(self, user_id, mode: bool):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"pdf_banner_mode": bool(mode)}},
            upsert=True
        )

    async def get_pdf_banner_mode(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("pdf_banner_mode", False) if user else False

    async def set_pdf_lock_mode(self, user_id, mode: bool):
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"pdf_lock_mode": bool(mode)}},
            upsert=True
        )

    async def get_pdf_lock_mode(self, user_id):
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("pdf_lock_mode", False) if user else False

DARKXSIDE78 = Database(Config.DB_URL, Config.DB_NAME)
