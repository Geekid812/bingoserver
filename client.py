import asyncio
import secrets
from datetime import datetime

from config import RECONNECT_TIMEOUT

SECRET_LENGTH = 16

# Represents the TCP connection between a client and the server
class ClientTCPSocket:
    def __init__(self, server, reader, writer):
        self.server = server
        self.reader = reader
        self.writer = writer
        self.secret = secrets.token_urlsafe(SECRET_LENGTH)[0:SECRET_LENGTH]
        self.opened = False
        self.created = datetime.utcnow()

        asyncio.create_task(self.connection())
    
    def matches(self, secret: str):
        return self.secret == secret

    async def write(self, message):
        if not self.opened: return
        self.writer.write(bytes(message + "\u0004", 'utf8'))
        await self.writer.drain()

    async def connection(self):
        self.opened = True

        await self.write(self.secret)
        asyncio.create_task(self.ping_loop())

        try:
            await self.reader.read() # Since we are not receiving data afterwards, this blocks until the socket is closed
        except ConnectionResetError: # Handle disconnect
            pass
        
        self.reader, self.writer = None, None # Drop reader and writer
        self.opened = False
        await asyncio.sleep(RECONNECT_TIMEOUT) # After this timeout, client is fully disconnected
        await self.server.remove_client(self)

    async def ping_loop(self):
        await asyncio.sleep(5)
        while self.opened and not self.reader.at_eof():
            await self.write("PING")
            await asyncio.sleep(30) # Ping every 30 seconds
