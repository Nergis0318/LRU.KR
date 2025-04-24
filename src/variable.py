from fastapi.templating import Jinja2Templates
import dotenv
import emoji

templates = Jinja2Templates(directory="templates")

emoji_data = emoji.EMOJI_DATA
emoji_data = emoji_data.items()
emoji_list = list()
for _ in emoji_data:
    emoji_list.append(_[0])

DOMAIN = dotenv.get_key("/.env", "DOMAIN")
DB = dotenv.get_key("/.env", "DB")
EMOJI_DB = dotenv.get_key("/.env", "EMOJI_DB")
KEY_DB = dotenv.get_key("/.env", "KEY_DB")
