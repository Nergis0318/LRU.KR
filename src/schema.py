from typing import Union

from pydantic import BaseModel, Field


class Link(BaseModel):
    url: str


class CustomLink(Link):
    custom_key: str


class LinkQRCODE(BaseModel):
    data: str
    version: Union[int, None] = Field(default=1, ge=1, le=40)
    error_correction: Union[int, None] = Field(default=0, ge=0, le=3)
    box_size: Union[int, None] = Field(default=10, ge=1, le=50)
    border: Union[int, None] = Field(default=4, ge=0, le=10)
    mask_pattern: Union[int, None] = Field(default=0, ge=0, le=7)


class TossUrl(BaseModel):
    bank_name: str
    account_number: str
    account_holder: str
