import asyncio
import logging
import os
import time
from typing import Any
from uuid import uuid4

import aiofiles
from aiohttp import BodyPartReader, web
from fhirpy import AsyncFHIRClient
from openai import AsyncOpenAI

from ..utils import minify_json_string
from ..utils.fhir import get_fhir_client


async def convert_handler(request: web.Request):
    questionnaire_id = request.rel_url.query["questionnaire"]
    token = request.headers["Authorization"]
    fhir_client: AsyncFHIRClient = get_fhir_client(token)
    questionnaire_reference = fhir_client.reference("Questionnaire", questionnaire_id)
    questionnaire = await questionnaire_reference.to_resource()
    openai_client: AsyncOpenAI = request.app["openai_client"]
    reader = await request.multipart()
    audio_content = await reader.next()
    if not audio_content:
        raise web.HTTPBadRequest()
    filepath = os.path.join(
        os.getcwd(),
        f"{int(time.time())}-{audio_content.filename}",  # type: ignore
    )
    async with aiofiles.open(filepath, "wb") as f:
        while True:
            chunk = await audio_content.read_chunk()
            if not chunk:
                break
            await f.write(chunk)
    questionnaire_response_id = str(uuid4())

    asyncio.create_task(
        generate_questionnaire_response_draft(
            openai_client,
            fhir_client,
            filepath,
            questionnaire,
            questionnaire_response_id,
        )
    )
    return web.HTTPOk()


async def generate_questionnaire_response_draft(
    openai_client: AsyncOpenAI,
    fhir_client: AsyncFHIRClient,
    filepath: str,
    questionnaire: Any,
    questionnaire_response_id: str,
):
    logging.error("Backjground task is started")
    logging.error("QuestionnaireResponse.id %s", questionnaire_response_id)
    transcription = await convert_audio_to_text(openai_client, filepath)
    logging.error("AUDIO WAS CONVERTED SUCCESSFULLY")
    os.remove(filepath)

    ai_generated_value = await get_ai_generated_value(
        openai_client, questionnaire, transcription
    )
    logging.error("AI assistant create response successfully")
    logging.error("ai_generated_value %s", ai_generated_value)
    await save_valid_resource(
        fhir_client, ai_generated_value, questionnaire_response_id
    )
    logging.error("FHIR QuestionnaireResponse was succesfully created")


async def convert_audio_to_text(client: AsyncOpenAI, filepath: str):
    # Use async access to file, provide content type to create
    audio_file = open(filepath, "rb")
    transcript = await client.audio.transcriptions.create(
        model="whisper-1", response_format="json", file=audio_file
    )
    # async with aiofiles.open(filepath, mode="rb") as f:
    #     audio_content_bytes = await f.read()
    #     audio_file_object = io.BytesIO(audio_content_bytes)
    #     logging.error("transcript.text %s", transcript.text)
    return transcript


async def get_assistant(client: AsyncOpenAI):
    instructions = """You are FHIR expert that accepts Questionnaire resource and the text with test clinical data.
You should create QuestionnaireResponse resource based on the provided text.
Your response should be a JSON string.
If text has no answers to fill out question item, leave it empty.
"""

    assistant_config = {
        "name": "FHAIR expert",
        "instructions": instructions,
        "model": "gpt-4-1106-preview",
    }
    assistant = await client.beta.assistants.retrieve("asst_uF5DlcVtI1aZoT0wO2DY9K0c")

    if assistant:
        assistant = await client.beta.assistants.update(
            assistant.id, **assistant_config
        )
    else:
        assistant = await client.beta.assistants.create(**assistant_config)

    return assistant


async def get_ai_generated_value(
    client: AsyncOpenAI, questionnaire: dict, transcription: str
):
    assistant = await get_assistant(client)
    thread = await client.beta.threads.create()
    content = f"""
You should create QuestionnaireResponse resource based on the provided text.

Questionnaire:
{questionnaire}

Text with test clinical data:
{transcription}
"""
    await client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=content
    )

    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # NOTE: Waits to run's success/failure completion status
    while True:
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )
        if run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            continue
        if run.status == "completed":
            result_messages = await client.beta.threads.messages.list(
                thread_id=thread.id
            )
            result_value = result_messages.data[0].content[0].text.value
            break
        raise Exception(f"Run {run.id} has status {run.status}")

    return result_value


async def save_valid_resource(
    client: AsyncFHIRClient, value: str, questionaire_response_id: str
):
    minified_value = minify_json_string(value)
    resource = client.resource(
        "QuestionnaireResponse",
        **minified_value,
        id=questionaire_response_id,
    )
    await resource.save()
    return resource
