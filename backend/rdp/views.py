import asyncio
import base64
import io
import os
import queue
import sys
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from aardwolf import logger
from aardwolf.keyboard import VK_MODIFIERS
from aardwolf.commons.factory import RDPConnectionFactory
from aardwolf.commons.iosettings import RDPIOSettings
from aardwolf.commons.queuedata import RDPDATATYPE
from aardwolf.commons.queuedata.keyboard import RDP_KEYBOARD_SCANCODE
from aardwolf.commons.queuedata.mouse import RDP_MOUSE
from aardwolf.commons.queuedata.constants import MOUSEBUTTON, VIDEO_FORMAT

router = APIRouter()

class RDPClientConsoleSettings:
    def __init__(self, url:str, iosettings:RDPIOSettings):
        self.mhover:int = True
        self.keyboard:int = True
        self.url:str = url
        self.iosettings:RDPIOSettings = iosettings
        # file path of the ducky file (if used)
        self.ducky_file = None
        # ducky script start delay, None means that typing will not start automatically
        self.ducky_autostart_delay = 5

class RDPImage:
    def __init__(self,x,y,image,width,height):
        self.x = x
        self.y = y
        self.image = image
        self.width = width
        self.height = height

class RDPClient:
    
    def __init__(self):
        url = os.getenv('RDP_URI', 'rdp+ntlm-password://PC:1234@192.168.101.14')

        width, height = "640X480".split('X')
        height = int(height)
        width = int(width)
        iosettings = RDPIOSettings()
        iosettings.video_width = width
        iosettings.video_height = height
        iosettings.video_bpp_min = 15 #servers dont support 8 any more :/
        iosettings.video_bpp_max = 32
        iosettings.video_out_format = VIDEO_FORMAT.PIL
        iosettings.client_keyboard = 'enus'

        settings = RDPClientConsoleSettings(url, iosettings)
        settings.mhover = None
        settings.keyboard = None
        settings.ducky_file = None
        settings.ducky_autostart_delay = None
        
        self.settings:RDPClientConsoleSettings = settings
        self.in_q = queue.Queue()
        self.conn = None
    
    def get_connection(self):
        return self.conn
    
    async def event_loop(self, websocket: WebSocket):
        while True:
            data = await self.conn.ext_out_queue.get()
            if data is None:
                break
            if data.type == RDPDATATYPE.VIDEO:
                image = data.data
                img_io = io.BytesIO()
                image.save(img_io, 'PNG')
                img_str = base64.b64encode(img_io.getvalue()).decode()
                ri = RDPImage(data.x, data.y, img_str, data.width, data.height)
                await websocket.send_json(ri.__dict__)
            elif data.type == RDPDATATYPE.CLIPBOARD_READY:
                continue
            elif data.type == RDPDATATYPE.CLIPBOARD_NEW_DATA_AVAILABLE:
                continue
            elif data.type == RDPDATATYPE.CLIPBOARD_CONSUMED:
                continue
            elif data.type == RDPDATATYPE.CLIPBOARD_DATA_TXT:
                continue
            else:
                logger.debug('Unknown incoming data: %s'% data)
            await asyncio.sleep(0.01)

    async def rdp_connection(self):
        rdpurl = RDPConnectionFactory.from_url(self.settings.url, self.settings.iosettings)
        self.conn = rdpurl.get_connection(self.settings.iosettings)
        print("conn", self.conn)
        _, err = await self.conn.connect()
        print("err", err)


def send_key(code, is_pressed):
    modifiers = VK_MODIFIERS(0)

    ki = RDP_KEYBOARD_SCANCODE()
    ki.keyCode = code
    ki.is_pressed = is_pressed
    if sys.platform == "linux":
        #why tho?
        ki.keyCode -= 8
    ki.modifiers = modifiers
    ki.vk_code = code

    return ki

def send_mouse(x, y, button, is_pressed):

    if button == -1:
        button = MOUSEBUTTON.MOUSEBUTTON_HOVER
    if button == 0:
        button = MOUSEBUTTON.MOUSEBUTTON_LEFT
    if button == 1:
        button = MOUSEBUTTON.MOUSEBUTTON_RIGHT
    if button == 2:
        button = MOUSEBUTTON.MOUSEBUTTON_MIDDLE
    if button == 3:
        button = MOUSEBUTTON.MOUSEBUTTON_WHEEL_UP
    if button == 4:
        button = MOUSEBUTTON.MOUSEBUTTON_WHEEL_DOWN

    mi = RDP_MOUSE()
    mi.xPos = x
    mi.yPos = y
    mi.button = button
    mi.is_pressed = is_pressed 
    
    return mi

@router.websocket("/rdp/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = RDPClient()
    await client.rdp_connection()
    conn = None


    asyncio.create_task(client.event_loop(websocket))

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get('event')
            if event == 'infos':
                print(data)
                conn = client.get_connection()
                print("infos", conn)
            elif event == 'mouse':
                x, y, button, is_pressed = data['x'], data['y'], data['button'], data['isPressed']
                print(data)
                mi = send_mouse(x, y, button, is_pressed)
                await conn.ext_in_queue.put(mi)
            elif event == 'wheel':
                x, y, step, is_negative, is_horizontal = data['x'], data['y'], data['step'], data['isNegative'], data['isHorizontal']
                print(data)
                mi = send_mouse(x, y, MOUSEBUTTON.MOUSEBUTTON_MIDDLE, False)
                await conn.ext_in_queue.put(mi)
            elif event == 'scancode':
                print(data)
                code, is_pressed = data['code'], data['isPressed']
                ki = send_key(code, is_pressed)
                await conn.ext_in_queue.put(ki)
            elif event == 'unicode':
                print(data)
                code, is_pressed = data['code'], data['isPressed']
                ki = send_key(code, is_pressed)
                await conn.ext_in_queue.put(ki)
            elif event == 'disconnect':
                await conn.terminate()
                break
    except WebSocketDisconnect:
        if conn:
            conn.terminate()

