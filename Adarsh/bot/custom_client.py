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
            # Get all the members of the DB_CHANNEL
            channel_info = await self.get_chat(DB_CHANNEL)
            chat_members = await client.get_chat_members(channel_info.id)
            chat_members_list = [member async for member in chat_members]
            
            for member in chat_members_list:
                if member.user:
                    try:
                        # Send the message to each member individually
                        await client.send_message(chat_id=member.user.id, text=message.text, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                    except Exception as e:
                        print(f"Error sending message to user {member.user.id}: {e}")
        except Exception as e:
            print(f"Error sending message to channel members: {e}")
