#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import ensure_future
from enum import Enum, auto
from ssl import SSLContext
from threading import Thread
from typing import Union

import janus
import websockets
from dataclasses import asdict, dataclass
from websockets import ConnectionClosed

from magic import async_new_game_plus, async_undead_curse


class Queue(janus.Queue):
    def get(self, **kwargs):
        return self.sync_q.get(**kwargs)

    def put(self, item, **kwargs):
        self.sync_q.put(item, **kwargs)

    async def async_get(self):
        return await self.async_q.get()

    async def async_put(self, item):
        await self.async_q.put(item)


class BlackBox(Thread):
    def __init__(self, max_size=0, **kwargs):
        super().__init__(**kwargs)
        self.max_size = max_size
        self.recv_queue: Union[Queue, None] = None
        self.send_queue: Union[Queue, None] = None
        self.loop: Union[asyncio.BaseEventLoop, None] = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.recv_queue = Queue(maxsize=self.max_size, loop=self.loop)
        self.send_queue = Queue(maxsize=self.max_size, loop=self.loop)


class ClientType(Enum):
    # @formatter:off
    master = 0
    slave = auto()
    def __str__(self):
        return self.name
    # @formatter:on


class ClientID(Enum):
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
    id: Union[ClientID, int]
    ssl_context: Union[SSLContext, None] = None

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.passwd = str(self.passwd)
        self.type = ClientType(self.type)
        self.id = ClientID(self.id)

    def __getitem__(self, item):
        items = tuple(asdict(self).values())
        return items[item]

    def __str__(self):
        template = '{0}://{1}:{2}/?passwd={3}&type={4}&id={5}'
        proto = 'ws' if self[-1] is None else 'wss'
        return template.format(proto, *self[:-1])


class Client(BlackBox):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @async_new_game_plus
    async def handle_recv_task(self, socket):
        item = await socket.recv()
        await self.recv_queue.async_put(item)

    @async_new_game_plus
    async def handle_send_task(self, socket):
        item = await self.send_queue.async_get()
        await socket.send(item)

    @async_undead_curse(5, print, ConnectionClosed, OSError)
    async def mainloop(self):
        async with websockets.connect(str(self.config), ssl=self.config[-1]) as socket:
            handle_recv_task = ensure_future(self.handle_recv_task(socket))
            handle_send_task = ensure_future(self.handle_send_task(socket))
            await asyncio.gather(handle_recv_task, handle_send_task)

    def run(self):
        super().run()
        self.loop.run_until_complete(self.mainloop())


if __name__ == '__main__':
    test_param = ClientConfig('localhost', 8080, '123456', 0, 0)
    test_client = Client(test_param)
    test_client.start()
