import base64
import asyncio
from typing import Optional, Callable, AsyncGenerator
import random

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
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

from src import (
    generate_emoji_key,
    generate_key,
    HTTP_404,
    generate_qr_code_image,
    generate_number_key,
    Link,
    LinkQRCODE,
    CustomLink,
    templates,
    Config,
    key_db_pool,
    emoji_db_pool,
)


app = FastAPI(
    title="sqla.re",
    summary="Made By Dev_Nergis(Backend, Frontend), ny64(Frontend)",
    description="sqla.re is a URL shortening service.",
    version="6.1.0",
)

api_key_header = APIKeyHeader(name="X-API-KEY")

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware)


async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != Config.CU_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return api_key


async def create_short_link(
    key_generator: Callable[[], AsyncGenerator[str, None]], pool, url: str
):
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
    icon_list = ["IMG_3937.jpg", "IMG_3938.jpg", "IMG_3939.jpg", "IMG_3940.png", "favicon.ico"]
    random_icon = random.choice(icon_list)
    print(random_icon)
    return FileResponse(f"static/{random_icon}", filename="favicon.ico")


@app.post("/shorten", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_link(body: Link):
    return await create_short_link(generate_key, key_db_pool, body.url)


@app.post("/shorten/number", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_number_link(body: Link):
    return await create_short_link(generate_number_key, key_db_pool, body.url)


@app.post("/shorten/emoji", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_emoji_link(body: Link):
    return await create_short_link(generate_emoji_key, emoji_db_pool, body.url)


@app.post("/shorten/custom", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_custom_link(body: CustomLink, api_key: str = Depends(get_api_key)):
    db = redis.Redis(connection_pool=key_db_pool)
    if await db.exists(body.custom_key):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Custom key already exists"
        )

    url_hash = base64.b85encode(body.url.encode())
    await db.json().set(body.custom_key, Path.root_path(), {"url": url_hash.hex()})
    return {"short_link": f"{Config.DOMAIN}/{body.custom_key}"}


@app.post("/shorten/qr", response_class=FileResponse, tags=["Shorten"])
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
    except:  # noqa: E722
        return HTTP_404(request)
