import io
import random
import string
from typing import AsyncGenerator

import qrcode
import valkey.asyncio as valkey

from .variable import db_pool, emoji_list, templates

redis_client = None
ascii_digits = string.ascii_letters + string.digits
digits = string.digits


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = valkey.Valkey(connection_pool=db_pool)
    return redis_client


# noinspection PyPep8Naming
def HTTP_404(request: object):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)  # pyright: ignore[reportArgumentType]


async def generate_key(length: int = 4, max_attempts: int = 5) -> AsyncGenerator[str, None]:
    db = await get_redis()

    # Batch generate candidates
    candidates = ["".join(random.choices(ascii_digits, k=length)) for _ in range(max_attempts)]

    # Check all candidates in single pipeline
    pipe = db.pipeline()
    for candidate in candidates:
        pipe.exists(candidate)
    results = await pipe.execute()

    # Return first non-existing key
    for candidate, exists in zip(candidates, results):
        if not exists:
            yield candidate
            return

    # All collided - increase length and retry
    async for key in generate_key(length + 1, max_attempts):
        yield key
        return


async def generate_number_key(length: int = 4, max_attempts: int = 5) -> AsyncGenerator[str, None]:
    db = await get_redis()

    # Batch generate candidates
    candidates = ["".join(random.choices(digits, k=length)) for _ in range(max_attempts)]

    # Check all candidates in single pipeline
    pipe = db.pipeline()
    for candidate in candidates:
        pipe.exists(candidate)
    results = await pipe.execute()

    # Return first non-existing key
    for candidate, exists in zip(candidates, results):
        if not exists:
            yield candidate
            return

    # All collided - increase length and retry
    async for key in generate_number_key(length + 1, max_attempts):
        yield key
        return


async def generate_emoji_key(length: int = 1, max_attempts: int = 5) -> AsyncGenerator[str, None]:
    db = await get_redis()

    # Batch generate candidates
    candidates = ["".join(random.choices(emoji_list, k=length)) for _ in range(max_attempts)]

    # Check all candidates in single pipeline
    pipe = db.pipeline()
    for candidate in candidates:
        pipe.exists(candidate)
    results = await pipe.execute()

    # Return first non-existing key
    for candidate, exists in zip(candidates, results):
        if not exists:
            yield candidate
            return

    # All collided - increase length and retry
    async for key in generate_emoji_key(length + 1, max_attempts):
        yield key
        return


# noinspection PyTypeChecker
def generate_qr_code_image(
    data: str,
    version: int = 1,
    error_correction: int = 0,
    box_size: int = 10,
    border: int = 4,
    mask_pattern: int = 0,
):
    img = qrcode.make(
        data,
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        image_factory=None,
        mask_pattern=mask_pattern,
    )
    img_byte_array = io.BytesIO()
    img.save(img_byte_array)
    img_byte_array.seek(0)
    return img_byte_array
