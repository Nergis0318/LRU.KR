import io
import random
import string
from typing import AsyncGenerator

import qrcode
import redis.asyncio as redis

from .variable import templates, emoji_list, db_pool

redis_client = None
ascii_digits = string.ascii_letters + string.digits
digits = string.digits


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(connection_pool=db_pool)
    return redis_client


# noinspection PyPep8Naming
def HTTP_404(request: object):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


async def generate_key(length: int = 4) -> AsyncGenerator[str, None]:
    db = await get_redis()
    while True:
        key = ''.join(random.choices(ascii_digits, k=length))
        if not await db.exists(key):
            yield key
            break
        length += 1


async def generate_number_key(length: int = 4) -> AsyncGenerator[str, None]:
    db = await get_redis()
    while True:
        key = ''.join(random.choices(digits, k=length))
        if not await db.exists(key):
            yield key
            break
        length += 1


async def generate_emoji_key(length: int = 4) -> AsyncGenerator[str, None]:
    db = await get_redis()
    while True:
        key = ''.join(random.choices(emoji_list, k=length))
        if not await db.exists(key):
            yield key
            break
        length += 1


# noinspection PyTypeChecker
def generate_qr_code_image(data: str, version: int = 1, error_correction: int = 0, box_size: int = 10, border: int = 4,
                           mask_pattern: int = 0):
    img = qrcode.make(data, version=version, error_correction=error_correction, box_size=box_size, border=border,
                      image_factory=None, mask_pattern=mask_pattern)
    img_byte_array = io.BytesIO()
    img.save(img_byte_array)
    img_byte_array.seek(0)
    return img_byte_array
