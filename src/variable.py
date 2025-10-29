from fastapi.templating import Jinja2Templates
import os
import emoji
import valkey.asyncio as valkey

templates = Jinja2Templates(directory="templates")

emoji_list = tuple(emoji.EMOJI_DATA.keys())


class Config:
    DOMAIN = os.environ.get("DOMAIN")
    DB = os.environ.get("DB")
    API_KEY = os.environ.get("API_KEY")

db_pool = valkey.ConnectionPool.from_url(Config.DB)
