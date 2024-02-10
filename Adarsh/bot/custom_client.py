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
            
            # List to hold all message sending tasks
            send_message_tasks = []
            for member in chat_members_list:
                if member.user:
                    # Start a task to send message to each member
                    task = asyncio.create_task(client.send_message(chat_id=member.user.id, text=message.text, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup))
                    send_message_tasks.append(task)

            # Wait for all message sending tasks to complete
            await asyncio.gather(*send_message_tasks)
        except Exception as e:
            print(f"Error sending message to channel members: {e}")

