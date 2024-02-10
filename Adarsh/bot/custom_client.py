# custom_client.py

from pyrogram import Client
from pyrogram.errors import FloodWait
import asyncio


class CustomClient(Client):
    def __init__(self, db_channel, *args, **kwargs):
        self.db_channel = db_channel
        super().__init__(*args, **kwargs)

    async def iter_chat_members(self, chat_id):
        """
        This method iterates over the members of a chat.
        
        :param chat_id: The ID of the chat whose members need to be iterated over.
        :return: An async iterator yielding the members of the chat.
        """
        offset = 0
        limit = 100  # Adjust the limit as per your requirement
        while True:
            try:
                members = await self.get_chat_members(chat_id, offset=offset, limit=limit)
                if not members:
                    break
                for member in members:
                    yield member
                offset += limit
            except Exception as e:
                print(f"Error fetching chat members: {e}")
                break
