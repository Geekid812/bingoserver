# Restricted routes authentification

from config import SECRET_KEY
from aiohttp import web

@web.middleware
async def authenticate(request, handler):
    if request.path.startswith("/internal/"):
        if "key" not in request.query: return web.Response(status=401)
        if request.query["key"] != SECRET_KEY: return web.Response(status=403)
    
    return await handler(request)
