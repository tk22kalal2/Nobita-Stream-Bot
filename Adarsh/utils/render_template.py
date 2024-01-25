from Adarsh.vars import Var
from Adarsh.bot import StreamBot
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.file_properties import get_file_ids
from Adarsh.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp


async def render_page(id, secure_hash):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash
    src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(id)}')
    
    if str(file_data.mime_type.split('/')[0].strip()) == 'video':
        async with aiofiles.open('Adarsh/template/req.html') as r:
            heading = 'Watch {}'.format(file_data.file_name)
            tag = file_data.mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)
    elif str(file_data.mime_type.split('/')[0].strip()) == 'audio':
        async with aiofiles.open('Adarsh/template/req.html') as r:
            heading = 'Listen {}'.format(file_data.file_name)
            tag = file_data.mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src)
    else:
        async with aiofiles.open('Adarsh/template/dl.html') as r:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    heading = 'Download {}'.format(file_data.file_name)
                    file_size = humanbytes(int(u.headers.get('Content-Length')))
                    html = (await r.read()) % (heading, file_data.file_name, src, file_size)
    current_url = f'{Var.URL}/{str(id)}/{file_data.file_name}?hash={secure_hash}'
    html_code = f'''
    <p>
    <center><h5>Click on 👇 button to watch/download in your favorite player</h5></center>
    <center>
                    <button class="magnet" onclick="vlc_player()"><img src="https://i.postimg.cc/15TQ4y7B/vlc.png"
                            alt="">watch in VLC PLAYER</button>
                    <button class="magnet" onclick="mx_player()"><img src="https://i.postimg.cc/sx4Msv4T/mx.png"
                            alt="">watch in MX PLAYER</button>
                    <button class="magnet" onclick="playit_player()"><img src="https://i.postimg.cc/RVGWYJFF/playit.png"
                            alt="">watch in PLAYit
                        PLAYER</button>
                    <button class="magnet" onclick="km_player()"><img src="https://i.postimg.cc/wT9tFQ9Z/km.png"
                            alt="">watch in KM PLAYER</button>
                    <button class="magnet" onclick="s_player()"><img src="https://i.postimg.cc/XYJr6NGg/s.png"
                            alt="">watch in S PLAYER</button>
                    <button class="magnet" onclick="hd_player()"><img src="https://i.postimg.cc/rFT43LNh/hd.png"
                            alt="">watch in HD
                        PLAYER(4K)</button>
                    <button class="magnet" onclick="bisalDownload()"><img style="height: 35px;"
                            src="https://i.postimg.cc/Zncc9YLq/Pngtree-download-icon-3581467.png" alt="">download video
                    </button>
    </center>
</p>

'''

    html += html_code    
    return html
