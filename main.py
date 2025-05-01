import base64
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    RedirectResponse,
    FileResponse,
)
from redis.commands.json.path import Path

from src.function import *
from src.schema import *
from src.variable import *
from src.zstd import ZstdMiddleware

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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# noinspection DuplicatedCode
@app.post("/shorten", response_class=ORJSONResponse)
async def shorten_link(body: Link):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.url.encode())

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), {"url": url_hash.hex()})
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}


# noinspection DuplicatedCode
@app.post("/shorten_emoji", response_class=ORJSONResponse)
async def shorten_emoji_link(body: Link):
    key = await anext(generate_emoji_key())
    url_hash = base64.b85encode(body.url.encode())

    db = redis.Redis(connection_pool=pool(EMOJI_DB))
    await db.json().set(key, Path.root_path(), {"url": url_hash.hex()})
    await db.close()

    return {"short_link": f"{DOMAIN}/{key}"}


# noinspection DuplicatedCode
@app.post("/shorten_qr_code", response_class=FileResponse)
async def generate_qr_code(body: LinkQRCODE, file: Optional[bool] = None):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.data.encode())
    hg_qs = {"url": url_hash.hex()}

    db = redis.Redis(connection_pool=pool(KEY_DB))
    await db.json().set(key, Path.root_path(), hg_qs)
    await db.close()

    img = generate_qr_code_image(
        f"{DOMAIN}/{key}",
        body.version,
        body.error_correction,
        body.box_size,
        body.border,
        body.mask_pattern,
    ).read()

    if file:
        return Response(img)
    else:
        return HTMLResponse(
            content=f'<img src="data:image/png;base64,{base64.b64encode(img).decode()}" />'
        )


# noinspection PyBroadException
@app.get("/{short_key}")
async def redirect_to_original(request: Request, short_key: str):
    db_c = redis.Redis(connection_pool=pool(KEY_DB))
    db = await db_c.json().jsonget(short_key, Path.root_path())
    await db_c.close()

    if db is None:
        db_c = redis.Redis(connection_pool=pool(EMOJI_DB))
        db = await db_c.json().jsonget(short_key, Path.root_path())
        await db_c.close()

    try:
        url = bytes.fromhex(db["url"]).decode("utf-8")
        url = base64.b85decode(url).decode("utf-8")
        return RedirectResponse(url)
    except:
        return HTTP_404(request)
