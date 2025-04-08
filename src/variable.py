from fastapi.templating import Jinja2Templates
import os
import emoji

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
