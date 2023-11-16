# (c) NobiDeveloper

import asyncio
import logging
from ..vars import Var
from pyrogram import Client
from Adarsh.utils.config_parser import TokenParser
from . import multi_clients, work_loads, StreamBot

class Bot(Client):
    def __init__(self):
        self.LOGGER = LOGGER
        self.db_channel = None  # Initialize db_channel attribute

    async def start(self):
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
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
                f"Make sure @{self.username} is an admin in the DB Channel, and double-check the CHANNEL_ID value. Current Value: {CHANNEL_ID}"
            )
            return 

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    
    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                bot_token=token,
                db_channel=Var.DB_CHANNEL,
                sleep_threshold=Var.SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
