#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import auto
from ssl import SSLContext
from typing import Union

from dataclasses import asdict, dataclass

from ground import Enum


class Status(Enum):
    master = 0
    slave = auto()

    def __neg__(self):
        is_master = (self == Status.master)
        return Status.slave if is_master else Status.master


class Subtype(Enum):
    normal = 0
    video = auto()
    audio = auto()


@dataclass
class ClientConfig:
    host: str
    port: int
    passwd: str
    status: Union[Status, int]
    subtype: Union[Subtype, int]
    ssl_context: Union[SSLContext, None] = None

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.passwd = str(self.passwd)
        self.status = Status(self.status)
        self.subtype = Subtype(self.subtype)

    def __getitem__(self, item):
        items = tuple(asdict(self).values())
        return items[item]

    def __str__(self):
        template = '{0}://{1}:{2}/?passwd={3}&status={4}&subtype={5}'
        proto = 'ws' if self[-1] is None else 'wss'
        return template.format(proto, *self[:-1])


@dataclass
class ServerConfig:
    host: str
    port: int
    passwd: str
    ssl_context: Union[SSLContext, None] = None

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.passwd = str(self.passwd)
