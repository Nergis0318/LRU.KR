import asyncio
import base64
from typing import Optional, Callable, AsyncGenerator

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import (
    HTMLResponse,
    ORJSONResponse,
    RedirectResponse,
    FileResponse,
)
from fastapi.security import APIKeyHeader
from valkey.commands.json.path import Path
from starlette.datastructures import URL

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
    get_redis,
)

app = FastAPI(
    title="LRU.KR",
    summary="Made By Dev_Nergis(Backend, Frontend), ny64(Frontend)",
    description="LRU.KR is a URL shortening service.",
    version="6.7.4",
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

api_key_header = APIKeyHeader(name="X-API-KEY")
root_path = Path.root_path()


async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != Config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return api_key


async def create_short_link(
    key_generator: Callable[[], AsyncGenerator[str, None]], url: str, domain: URL
):
    key = await anext(key_generator())
    url_hash = base64.b85encode(url.encode()).hex()

    db = await get_redis()
    await db.json().set(key, root_path, {"url": url_hash})

    return {"short_link": str(domain) + key}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico", filename="favicon.ico")


@app.get("/robots.txt")
async def robots():
    return FileResponse("static/robots.txt", filename="robots.txt")


@app.post("/api/shorten", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_link(request: Request, body: Link):
    return await create_short_link(generate_key, body.url, request.base_url)


@app.post("/api/shorten/number", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_number_link(request: Request, body: Link):
    return await create_short_link(generate_number_key, body.url, request.base_url)


@app.post("/api/shorten/emoji", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_emoji_link(request: Request, body: Link):
    return await create_short_link(generate_emoji_key, body.url, request.base_url)


# noinspection PyUnusedLocal
@app.post("/api/shorten/custom", response_class=ORJSONResponse, tags=["Shorten"])
async def shorten_custom_link(
    request: Request, body: CustomLink, api_key: str = Depends(get_api_key)
):
    db = await get_redis()
    if await db.exists(body.custom_key):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Custom key already exists"
        )

    url_hash = base64.b85encode(body.url.encode()).hex()
    await db.json().set(body.custom_key, root_path, {"url": url_hash})
    return {"short_link": request.base_url + body.custom_key}


@app.post("/api/shorten/qr", response_class=FileResponse, tags=["Shorten"])
async def generate_qr_code(
    request: Request, body: LinkQRCODE, file: Optional[bool] = None
):
    key = await anext(generate_key())
    url_hash = base64.b85encode(body.data.encode()).hex()

    db = await get_redis()
    await db.json().set(key, root_path, {"url": url_hash})

    img_bytes = await asyncio.to_thread(
        generate_qr_code_image,
        request.base_url + key,
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


@app.get("/{short_key}", tags=["Redirect"])
async def redirect_to_original(request: Request, short_key: str):
    db = await get_redis()
    data = await db.json().get(short_key, root_path)

    try:
        return RedirectResponse(
            base64.b85decode(bytes.fromhex(data["url"])).decode("utf-8")
        )
    except:  # noqa: E722
        return HTTP_404(request)
