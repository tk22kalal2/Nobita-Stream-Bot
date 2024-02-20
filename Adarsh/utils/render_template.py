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
    <button style="width: 240px; height: 50px; border-radius: 6px; border: none; color: #1b94e7; background: #1a1b1f; font-size: 16px; cursor: pointer; font-weight: 600; box-shadow: 10px 10px 10px -1px rgba(10, 99, 169, 0.16), -10px -10px 10px -1px rgba(255, 255, 255, 0.70);" onclick="window.location.href = 'intent:{current_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_data.file_name};end'">
    <i class="fa-solid fa-play" style="margin-right: 10px;"></i>
    MX-Player
    </button>
    <button style="width: 240px; height: 50px; border-radius: 6px; border: none; color: #1b94e7; background: #1a1b1f; font-size: 16px; cursor: pointer; font-weight: 600; box-shadow: 10px 10px 10px -1px rgba(10, 99, 169, 0.16), -10px -10px 10px -1px rgba(255, 255, 255, 0.70);" onclick="window.location.href = 'vlc://{current_url}'">
    <i class="fa-solid fa-circle-play" style="margin-right: 10px;"></i>
    VLC-Player
    </button>
    <button style="width: 240px; height: 50px; border-radius: 6px; border: none; color: #1b94e7; background: #1a1b1f; font-size: 16px; cursor: pointer; font-weight: 600; box-shadow: 10px 10px 10px -1px rgba(10, 99, 169, 0.16), -10px -10px 10px -1px rgba(255, 255, 255, 0.70);" onclick="window.location.href = 'playit://playerv2/video?url={current_url}&amp;title={file_data.file_name}'">
    <i class="fa-solid fa-file-video" style="margin-right: 10px;"></i>
    Playit-Player
    </button>
    
    <br><br> <!-- Add vertical gap here -->
        
    <button style="border: 0; padding: 0; width: 300px; height: 40px; font-size: 20px; background-color: blue; border-radius: 0; border-bottom-left-radius: 5px; border-top-left-radius: 5px; border-bottom-right-radius: 5px; border-top-right-radius: 5px; padding: 0; color: white;" onclick="window.location.href = '{current_url}'">Download Now</button>
    
    </center>
</p>
    <a href="//www.dmca.com/Protection/Status.aspx?ID=fea8fffa-2c9a-41c1-a05b-8235f4492291" title="DMCA.com Protection Status" class="dmca-badge"> <img src ="https://images.dmca.com/Badges/DMCA_logo-std-btn120w.png?ID=fea8fffa-2c9a-41c1-a05b-8235f4492291"  alt="DMCA.com Protection Status" /></a>  <script src="https://images.dmca.com/Badges/DMCABadgeHelper.min.js"> </script>
'''

    html += html_code    
    return html
