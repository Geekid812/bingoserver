from aiohttp import web

@web.middleware
async def logging(request, handler):
    info = f"{request.version} {request.method} {request.path} {await request.text()} :"
    res = await handler(request)
    info += f" {res.status} {res.text}"
    print(info)
    return res
