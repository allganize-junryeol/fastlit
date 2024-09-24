import asyncio
import json
import os
import struct
import socket
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import paramiko

router = APIRouter()

import re

def parse_ssh_uri(uri):
    # 정규 표현식으로 URI 파싱
    pattern = r"ssh://(?:(?P<username>[^:]+)(?::(?P<password>[^@]+))?@)?(?P<ip>[^:]+)(?::(?P<port>\d+))?"
    match = re.match(pattern, uri)
    
    if match:
        # 매칭된 그룹을 딕셔너리로 반환
        return {
            "username": match.group("username"),
            "password": match.group("password"),
            "ip": match.group("ip"),
            "port": int(match.group("port")) if match.group("port") else 22,
        }
    else:
        return None

class SSHClient:
    def __init__(
            self,
        ) -> None:
        
        uri = os.getenv('SSH_URI', 'ssh://PC:1234@0.0.0.0')
        data = parse_ssh_uri(uri)

        self.BUF_SIZE = 32 * 1024

        self.entrypoint_ip = data["ip"]
        self.entrypoint_port = data["port"]
        self.entrypoint_username = data["username"]
        self.entrypoint_password = data["password"]

        self.internel_ip = "localhost"
        self.internel_port = 22
        self.internel_username = data["username"]
        self.internel_password = data["password"]

        self.phost = paramiko.SSHClient()
        self.jhost = paramiko.SSHClient()

        self.pchannel = None
        self.jchannel = None

        self.connect()

    def connect(self):
        try:
            self.phost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.phost.connect(
                self.entrypoint_ip, self.entrypoint_port, 
                username=self.entrypoint_username, 
                password=self.entrypoint_password, 
                timeout=10
            )

            transport = self.phost.get_transport()
            self.pchannel = transport.open_channel(
                "direct-tcpip", (self.internel_ip, self.internel_port), (self.entrypoint_ip, self.entrypoint_port)
            )
            self.pchannel.setblocking(0)

            self.jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.jhost.connect(
                self.internel_ip, self.internel_port, 
                username=self.internel_username, 
                password=self.internel_password, 
                sock=self.pchannel, 
                timeout=10
            )
        except socket.error:
            raise ValueError('Unable to connect.')
        except paramiko.BadAuthenticationType:
            raise ValueError('Bad authentication type.')
        except paramiko.AuthenticationException:
            raise ValueError('Authentication failed.')
        except paramiko.BadHostKeyException:
            raise ValueError('Bad host key.')

        self.jchannel = self.jhost.invoke_shell(term='xterm')
        self.jchannel.setblocking(0)
    
    def close(self):
        self.jchannel.close()
        self.jhost.close()
        self.pchannel.close()
        self.phost.close()

    def read(self):
        try:
            data = self.jchannel.recv(self.BUF_SIZE)
            if data:
                return data.decode()
        except OSError:
            if self.pchannel.closed or self.jchannel.closed:
                raise WebSocketDisconnect

    def write(self, msg: str):
        try:
            data = msg.encode()
            self.jchannel.send(msg)
        except OSError:
            if self.pchannel.closed or self.jchannel.closed:
                raise WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def event_loop(self, websocket: WebSocket, client: SSHClient):
        while True:
            message = client.read()
            if message:
                await websocket.send_text(message)
            await asyncio.sleep(0.01)


manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    print(client_id, websocket)
    
    await manager.connect(websocket)

    connection = SSHClient(
        # entrypoint_ip = "127.0.0.1",
        # entrypoint_username = 'junryeol',
        # entrypoint_password = 'qkrwns23',
        # internel_ip = "192.168.101.18",
        # internel_username = 'junryeol',
        # internel_password = 'qkrwns23',
    )

    try:
        asyncio.create_task(manager.event_loop(websocket, connection))
        while True:
            msg: str = await websocket.receive_text()
            data: dict = json.loads(msg)

            resize = data.get('resize')
            if resize and len(resize) == 2:
                try:
                    connection.jchannel.resize_pty(*resize)
                except (TypeError, struct.error, paramiko.SSHException):
                    pass

            message = data.get("data")
            if message:
                connection.write(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        connection.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    