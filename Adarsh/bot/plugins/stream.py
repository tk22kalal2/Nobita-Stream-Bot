#(c) NobiDeveloper
import os
import asyncio
from asyncio import TimeoutError
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telethon.tl.types import InputPeerChannel
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.name)

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)
MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

from pyrogram import Client
from pyrogram.errors import FloodWait

class Bot(Client):
    def __init__(self):
        self.LOGGER = LOGGER
        self.db_channel = None  # Initialize db_channel attribute

    async def start(self):
        try:
            db_channel = await self.get_chat(Var.DB_CHANNEL)
            self.db_channel = db_channel
            test_message = await self.send_message(
                chat_id=db_channel.id,
                text="Test Message",
                disable_notification=True
            )
            await test_message.delete()
            self.LOGGER(__name__).info(
                f"CHANNEL_ID Database detected!\n┌ Title: {db_channel.title}\n└ Chat ID: {db_channel.id}\n——"
            )
        except FloodWait as e:
            self.LOGGER(__name__).warning(f"FloodWait: {e}")
        except Exception as e:
            self.LOGGER(__name__).error(f"Error during Bot initialization: {e}")
            self.LOGGER(__name__).warning(
                f"Make sure @{self.username} is an admin in the DB Channel, and double-check the CHANNEL_ID value. Current Value: {Var.DB_CHANNEL}"
            )

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages : total_messages + 200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except BaseException:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    if (
        message.forward_from_chat
        and message.forward_from_chat.id == client.db_channel.id
    ):
        return message.forward_from_message_id
    elif message.forward_from_chat or message.forward_sender_name or not message.text:
        return 0
    else:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        elif channel_id == client.db_channel.username:
            return msg_id
            
@StreamBot.on_message(filters.private & filters.user(list(Var.OWNER_ID)) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            # Prompt the user to provide the first message from the DB Channel
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return  # Return if there's an exception (e.g., timeout)

        # Get the message ID from the provided message or link
        f_msg_id = await get_message_id(client, first_message)

        if f_msg_id:
            break
        else:
            # Inform the user of an error if the message/link is not from the DB Channel
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            # Prompt the user to provide the last message from the DB Channel
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return  # Return if there's an exception (e.g., timeout)

        # Get the message ID from the provided message or link
        s_msg_id = await get_message_id(client, second_message)

        if s_msg_id:
            break
        else:
            # Inform the user of an error if the message/link is not from the DB Channel
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    message_links = []
    for msg_id in range(min(f_msg_id, s_msg_id), max(f_msg_id, s_msg_id) + 1):
        try:
            # Forward the message to BIN_CHANNEL
            log_msg = await client.forward_messages(
                chat_id=Var.BIN_CHANNEL,
                from_chat_id=client.db_channel.id,
                message_ids=msg_id,
            )

            # Generate links for the forwarded message
            stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            link = f"Here is a link for the forwarded message:\n{stream_link}\n{online_link}"
            message_links.append(link)

        except Exception as e:
            print(f"Error forwarding message: {e}")

    # Send the generated links to the user
    for link in message_links:
        await message.reply(link)

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo) , group=4)    
async def private_receive_handler(c: Client, m: Message):
    if bool(CUSTOM_CAPTION) & bool(m.video):
        caption = CUSTOM_CAPTION.format(previouscaption="" if not m.caption else m.caption.html, filename=m.video.file_name)
    else:
        caption = "" if not m.caption else m.caption.html
    
    try:
        log_msg = await c.send_message(chat_id=Var.BIN_CHANNEL, text=caption)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                
        X = await log_msg.reply_text(text=f"{caption} \n**Stream ʟɪɴᴋ :** {stream_link}", disable_web_page_preview=True, quote=True)
        try:
            await X.forward(chat_id=Var.DB_CHANNEL)
        except Exception as e:
            print(f"Error forwarding message to DB_CHANNEL: {e}")                 
        await m.reply_text(
            text=f"{get_name(log_msg)} \n**Stream ʟɪɴᴋ :** {stream_link}", disable_web_page_preview=True, quote=True
        )    
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True)
@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo)  & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(broadcast.chat.id)
        if check_pass == None:
            await broadcast.reply_text("Login first using /login cmd \n don\'t know the pass? request it from developer!")
            return
        if check_pass != MY_PASS:
            await broadcast.reply_text("Wrong password, login again")
            await pass_db.delete_user(broadcast.chat.id)
            
            return
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**ʀᴇǫᴜᴇꜱᴛ ᴜʀʟ:** {stream_link}",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🖥️  ꜱᴛʀᴇᴀᴍ  🖥️", url=stream_link),
                     InlineKeyboardButton('📥  ᴅᴏᴡɴʟᴏᴀᴅ  📥', url=online_link)],
                    [InlineKeyboardButton('🎪  ꜱᴜʙꜱᴄʀɪʙᴇ ᴍʏ ʏᴛ ᴄʜᴀɴɴᴇʟ  🎪', url='https://youtube.com/@NobiDeveloper')]
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"GOT FLOODWAIT OF {str(w.x)}s FROM {broadcast.chat.title}\n\n**CHANNEL ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ERROR_TRACKEBACK:** `{e}`", disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Give me edit permission in updates and bin Channel!{e}**")
