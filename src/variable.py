import os
import socket

import emoji
import valkey.asyncio as valkey
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

emoji_list = tuple(emoji.EMOJI_DATA.keys())


class Config:
    DB = os.environ.get("DB")
    API_KEY = os.environ.get("API_KEY")


db_pool = valkey.ConnectionPool.from_url(
    Config.DB,  # pyright: ignore[reportArgumentType]
    max_connections=50,
    socket_keepalive=True,
    socket_keepalive_options={
        socket.TCP_KEEPIDLE: 60,
        socket.TCP_KEEPINTVL: 10,
        socket.TCP_KEEPCNT: 3,
    },
    retry_on_timeout=True,
    health_check_interval=30,
)
