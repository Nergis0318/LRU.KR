from typing import Union

from pydantic import BaseModel


class Link(BaseModel):
    url: str


class CustomLink(Link):
    custom_key: str


class LinkQRCODE(BaseModel):
    data: str
    version: Union[int, None] = 1
    error_correction: Union[int, None] = 0
    box_size: Union[int, None] = 10
    border: Union[int, None] = 4
    mask_pattern: Union[int, None] = 0
