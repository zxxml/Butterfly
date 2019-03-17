#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import ensure_future

import websockets
from websockets import ConnectionClosed

from config import ClientConfig
from ground import BlackBox
from magic import async_new_game_plus, async_undead_curse


class Client(BlackBox):
    def __init__(self, config: ClientConfig, **kwargs):
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
