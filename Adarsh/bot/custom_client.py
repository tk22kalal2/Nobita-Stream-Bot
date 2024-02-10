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
            chat_members = await self.get_chat_members(self.db_channel)
            for member in chat_members:
                try:
                    # Forward the message to each member
                    await message.forward(member.user.id)
                    await asyncio.sleep(0.5)  # Sleep briefly to avoid flooding
                except FloodWait as e:
                    print(f"Sleeping for {str(e.x)}s")
                    await asyncio.sleep(e.x)
                except Exception as e:
                    print(f"Error forwarding message to user {member.user.id}: {e}")
        except Exception as e:
            print(f"Error getting chat members: {e}")

