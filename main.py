import base64
import asyncio
from typing import Optional, Callable, Awaitable, AsyncGenerator
import random

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    RedirectResponse,
    FileResponse,
)
import redis.asyncio as redis
from redis.commands.json.path import Path

from src import *


app = FastAPI(
    title="sqla.re",
    summary="Made By Dev_Nergis(Backend, Frontend), ny64(Frontend)",
    description="sqla.re is a URL shortening service.",
    version="6.0.0",
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware)


async def create_short_link(key_generator: Callable[[], AsyncGenerator[str, None]], pool, url: str):
    key = await anext(key_generator())
    url_hash = base64.b85encode(url.encode())

    db = redis.Redis(connection_pool=pool)
    await db.json().set(key, Path.root_path(), {"url": url_hash.hex()})

    return {"short_link": f"{Config.DOMAIN}/{key}"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    icon_list = ["IMG_3937.jpg", "IMG_3938.jpg", "IMG_3939.jpg", "IMG_3940.png"]
    random_icon = random.choice(icon_list)
    print(random_icon)
    return FileResponse(f"static/{random_icon}", filename="favicon.ico")


@app.post("/shorten", response_class=ORJSONResponse)
async def shorten_link(body: Link):
    return await create_short_link(generate_key, key_db_pool, body.url)


@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    return await create_short_link(generate_emoji_key, emoji_db_pool, body.url)


@app.post("/shorten_qr_code", response_class=FileResponse)
async def generate_qr_code(body: LinkQRCODE, file: Optional[bool] = None):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.data.encode())
    hg_qs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=key_db_pool)
    await db.json().set(key, Path.root_path(), hg_qs)

    img_bytes = await asyncio.to_thread(
        generate_qr_code_image,
        f"{Config.DOMAIN}/{key}",
        body.version,
        body.error_correction,
        body.box_size,
        body.border,
        body.mask_pattern,
    )

    if file:
        return Response(img_bytes.getvalue())
    else:
        return HTMLResponse(
            content=f'<img src="data:image/png;base64,{base64.b64encode(img_bytes.getvalue()).decode()}" />'
        )


# noinspection PyBroadException
@app.get("/{short_key}")
async def redirect_to_original(request: Request, short_key: str):
    db_c = redis.Redis(connection_pool=key_db_pool)
    db = await db_c.json().jsonget(short_key, Path.root_path())

    if db is None:
        db_c = redis.Redis(connection_pool=emoji_db_pool)
        db = await db_c.json().jsonget(short_key, Path.root_path())

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
        return RedirectResponse(url)
    except:
        return HTTP_404(request)
