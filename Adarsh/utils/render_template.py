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
        <button style="font-size: 0; border: 0; padding: 0; position: relative;" onclick="window.location.href = 'intent:{current_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_data.file_name};end'">
            <img src="https://graph.org/file/7b4dbee176ae1d20442db.jpg" alt="MX Player Logo" style="width: 100%; height: auto;">
            <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: white; font-weight: bold;">MX PLAYER</span>
        </button>

        <button style="font-size: 20px; border: 0; padding: 0; color: darkred; font-weight: bold;" onclick="window.location.href = 'vlc://{current_url}'">
            <img src="https://graph.org/file/04975212d154e55472969.jpg" alt="VLC Logo" style="width: 30px; height: 30px; margin-right: 10px;">
            VLC player
        </button>

        <br><br> <!-- Add vertical gap here -->

        <button style="font-size: 20px; border: 0; padding: 0; color: orange; font-weight: bold;" onclick="window.location.href = 'playit://playerv2/video?url={current_url}&amp;title={file_data.file_name}'">
            <img src="https://graph.org/file/f098afd1dd1715afcbc96.jpg" alt="Playit Logo" style="width: 30px; height: 30px; margin-right: 10px;">
            Playit player
        </button>&nbsp; <br>

        <br><br> <!-- Add vertical gap here -->
        
        <button style="font-size: 20px; background-color: blue; border: 2px solid black; border-radius: 0 20px 0 20px; padding: 10px; color: white;" onclick="window.location.href = '{current_url}'">____Download Now____</button>
    </center>
</p>

'''

    html += html_code    
    return html
