# (c) NobiDeveloper
from pyrogram import Client
import pyromod.listen
from ..vars import Var
from os import getcwd
from .bot import CustomClient  # Assuming custom_client.py is in the same directory

StreamBot = CustomClient(
    db_channel=Var.DB_CHANNEL,
    name='Web Streamer',
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS
)

multi_clients = {}
work_loads = {}
