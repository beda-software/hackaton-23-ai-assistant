from aiohttp import web
from openai import AsyncOpenAI

from . import config
from .handlers import convert_handler


async def on_startup(app: web.Application):
    app["openai_client"] = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def application():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.router.add_post("/convert", convert_handler)

    return app
