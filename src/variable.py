import os

import emoji
import valkey.asyncio as valkey
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

emoji_list = tuple(emoji.EMOJI_DATA.keys())


class Config:
    DB = os.environ.get("DB")
    API_KEY = os.environ.get("API_KEY")


db_pool = valkey.ConnectionPool.from_url(Config.DB)
