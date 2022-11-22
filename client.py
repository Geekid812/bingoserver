import asyncio
import secrets

SECRET_LENGTH = 16

# Represents the TCP connection between a client and the server
class ClientTCPSocket:
    def __init__(self, server, reader, writer):
        self.server = server
        self.reader = reader
        self.writer = writer
        self.secret = secrets.token_urlsafe(SECRET_LENGTH)[0:SECRET_LENGTH]
        self.closed = False

        asyncio.create_task(self.connection())
    
    def matches(self, secret: str):
        return self.secret == secret

    async def write(self, message):
        if self.writer is None: return
        self.writer.write(bytes(message + "\u0004", 'utf8'))
        await self.writer.drain()

    async def connection(self):
        await self.write(self.secret)
        asyncio.create_task(self.ping_loop())

        try:
            await self.reader.read() # Since we are not receiving data afterwards, this blocks until the socket is closed
        except ConnectionResetError: # Handle disconnect
            pass
        
        self.writer.close()
        self.reader, self.writer = None, None
        if not self.closed: # skip if already closed
            await asyncio.sleep(30) # Allow reconnection for 30 seconds
            if self in self.server.clients:
                await self.server.remove_client(self)


    async def ping_loop(self):
        await asyncio.sleep(5)
        while self.reader and not self.reader.at_eof():
            await self.write("PING")
            await asyncio.sleep(30) # Ping every 30 seconds
