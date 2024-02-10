# custom_client.py

from pyrogram import Client
from pyrogram.errors import FloodWait
import asyncio


class CustomClient(Client):
    def __init__(self, db_channel, *args, **kwargs):
        self.db_channel = db_channel
        super().__init__(*args, **kwargs)

    async def forward_message_to_all_users(self, message):
        try:
            # Get all members of the specified chat
            channel_info = await self.get_chat(self.db_channel)
            async for member in self.iter_chat_members(channel_info.id):
                if member.user:
                    # Forward the message to each member
                    await message.forward(member.user.id)
                    await asyncio.sleep(0.5)  # Sleep briefly to avoid flooding
        except FloodWait as e:
            print(f"Sleeping for {str(e.x)}s")
            await asyncio.sleep(e.x)
        except Exception as e:
            print(f"Error forwarding message to channel members: {e}")

