# (c) NobiDeveloper
from pyrogram import Client
import pyromod.listen
from ..vars import Var
from os import getcwd

def __init__(self, db_channel, *args, **kwargs):
        self.db_channel = db_channel
        super().__init__(*args, **kwargs)
    
StreamBot = Client(
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
