import os
import time

import aiofiles
from aiohttp import BodyPartReader, web
from openai import AsyncOpenAI


async def convert_handler(request: web.Request):
    openai_client: AsyncOpenAI = request.app["openai_client"]
    reader = await request.multipart()
    audio_content = await reader.next()
    if not audio_content:
        raise web.HTTPBadRequest()
    filepath = os.path.join(
        os.getcwd(),
        f"{int(time.time())}-{audio_content.filename}",  # type: ignore
    )
    transcription = await convert_audio_to_text(openai_client, filepath, audio_content)
    os.remove(filepath)

    return web.json_response({"text": transcription.text})


async def convert_audio_to_text(
    client: AsyncOpenAI, filepath: str, content: BodyPartReader
):
    async with aiofiles.open(filepath, "wb") as f:
        while True:
            chunk = await content.read_chunk()
            if not chunk:
                break
            await f.write(chunk)
        # Use async access to file, provide content type to create
        # To prevent unrecognized file extension error
    audio_file = open(filepath, "rb")
    transcript = await client.audio.transcriptions.create(
        model="whisper-1", response_format="json", file=audio_file
    )
    # async with aiofiles.open(filepath, mode="rb") as f:
    #     audio_content_bytes = await f.read()
    #     audio_file_object = io.BytesIO(audio_content_bytes)
    #     logging.error("transcript.text %s", transcript.text)
    return transcript