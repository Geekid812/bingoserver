import asyncio

# Represents the TCP connection between a client and the server
class ClientTCPSocket:
    def __init__(self, server, reader, writer):
        self.server = server
        self.reader = reader
        self.writer = writer
        self.login = ""

        asyncio.create_task(self.connection())
    
    def matches(self, login: str):
        return self.login == login

    async def write(self, message):
        self.writer.write(bytes(message + "\u0004", 'utf8'))
        await self.writer.drain()

    async def connection(self):
        self.login = (await self.reader.readline()).decode('utf8').strip() # Receive login
        await self.write("OK")
        asyncio.create_task(self.ping_loop())

        await self.reader.read() # Since we are not receiving data afterwards, this blocks until the socket is closed
        await self.server.disconnect(self)

    async def ping_loop(self):
        await asyncio.sleep(5)
        while not self.reader.at_eof():
            await self.write("PING")
            await asyncio.sleep(30) # Ping every 30 seconds
