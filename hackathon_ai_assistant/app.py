import aiohttp_cors
from aiohttp import web
from openai import AsyncOpenAI

from . import config
from .handlers import convert_handler


async def on_startup(app: web.Application):
    app["openai_client"] = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


def application():
    app = web.Application()
    app.on_startup.append(on_startup)
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    cors.add(app.router.add_post("/convert", convert_handler))

    return app
