#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import Enum, auto
from ssl import SSLContext
from typing import Union

from dataclasses import asdict, dataclass


class ClientType(Enum):
    # @formatter:off
    master = 0
    slave = auto()
    def __str__(self):
        return self.name
    # @formatter:on


class ClientSubtype(Enum):
    # @formatter:off
    normal = 0
    video = auto()
    audio = auto()
    def __str__(self):
        return self.name
    # @formatter:on


@dataclass
class ClientConfig:
    host: str
    port: int
    passwd: str
    type: Union[ClientType, int]
    subtype: Union[ClientSubtype, int]
    ssl_context: Union[SSLContext, None] = None

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.passwd = str(self.passwd)
        self.type = ClientType(self.type)
        self.subtype = ClientSubtype(self.subtype)

    def __getitem__(self, item):
        items = tuple(asdict(self).values())
        return items[item]

    def __str__(self):
        template = '{0}://{1}:{2}/?passwd={3}&type={4}&subtype={5}'
        proto = 'ws' if self[-1] is None else 'wss'
        return template.format(proto, *self[:-1])
