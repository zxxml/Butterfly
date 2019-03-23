#!/usr/bin/python3
# -*- coding: utf-8 -*-
from asyncio import ensure_future, gather
from enum import auto as enum_auto
from ssl import SSLContext
from typing import Union

from dataclasses import asdict, dataclass
from websockets import ConnectionClosed, connect

from core.ground import BlackBox, Enum
from core.magic import async_new_game_plus, async_undead_curse


class Status(Enum):
    """客户端的地位是服务器决定分组的转发目标的关键。
    它只有两种选项：master和slave，对任一地位取反可以获得另一地位。
    """
    master = enum_auto()
    slave = enum_auto()

    def __neg__(self):
        is_master = (self == Status.master)
        return Status.slave if is_master else Status.master


class Subtype(Enum):
    """客户端的子类型是服务器决定分组的转发目标的关键。
    它有三种选项：normal、video和audio。
    """
    normal = enum_auto()
    video = enum_auto()
    audio = enum_auto()


@dataclass
class ClientConfig:
    host: str
    port: int
    passwd: str
    status: Union[Status, str]
    subtype: Union[Subtype, str]
    ssl_context: SSLContext = None

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


class Client(BlackBox):
    def __init__(self, config: ClientConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @async_new_game_plus
    async def recv_task(self, socket):
        item = await socket.recv()
        await self.recv_queue.async_put(item)

    @async_new_game_plus
    async def send_task(self, socket):
        item = await self.send_queue.async_get()
        await socket.send(item)

    @async_undead_curse(5, print, ConnectionClosed, OSError)
    async def mainloop(self):
        async with connect(str(self.config), ssl=self.config[-1]) as socket:
            recv_task = ensure_future(self.recv_task(socket))
            send_task = ensure_future(self.send_task(socket))
            await gather(recv_task, send_task)

    def run(self):
        self.loop.run_until_complete(self.mainloop())
