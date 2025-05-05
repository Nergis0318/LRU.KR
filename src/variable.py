from fastapi.templating import Jinja2Templates
import os
import emoji
import redis.asyncio as redis

templates = Jinja2Templates(directory="templates")

emoji_data = emoji.EMOJI_DATA
emoji_data = emoji_data.items()
emoji_list = list()
for _ in emoji_data:
    emoji_list.append(_[0])


class Config():
    DOMAIN = os.environ.get("DOMAIN")
    DB = os.environ.get("DB")
    EMOJI_DB = os.environ.get("EMOJI_DB")
    KEY_DB = os.environ.get("KEY_DB")
    CU_KEY = os.environ.get("CU_KEY")

key_db_pool = redis.ConnectionPool.from_url(f"{Config.DB}/{Config.KEY_DB}")
emoji_db_pool = redis.ConnectionPool.from_url(f"{Config.DB}/{Config.EMOJI_DB}")
