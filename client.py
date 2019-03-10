#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import ensure_future

import websockets
from websockets import ConnectionClosed

from config import Client as _Client
from message import Message, MessageQueue
from utiliy import undead_curse


class Client(_Client):
    """客户端的基本形态，这个基本形态将帮助管理一部分琐事，例如：断线重连。"""

    @staticmethod
    def get_server_url(host, port, passwd, client_type, ssl_context):
        protocol = 'ws' if ssl_context is None else 'wss'
        return Client.url_template.format(protocol, host, port, passwd, client_type)

    def __init__(self, host, port, passwd, client_type, ssl_context=None):
        super().__init__()
        self.server_url = Client.get_server_url(host, port, passwd, client_type, ssl_context)
        self.ssl_context = ssl_context
        self.recv_queue = None
        self.send_queue = None

    async def recv_task(self, conn):
        while True:
            msg = await conn.recv()
            msg = Message.unpack(msg)
            await self.recv_queue.async_put(msg)

    async def send_task(self, conn):
        while True:
            msg = await self.send_queue.async_get()
            await conn.send(msg.pack())

    @undead_curse(_Client.restart_interval, ConnectionClosed, OSError)
    def mainloop(self, new_loop=False):
        async def _mainloop():
            self.recv_queue = MessageQueue()
            self.send_queue = MessageQueue()
            async with websockets.connect(self.server_url, ssl=self.ssl_context) as conn:
                recv_task = ensure_future(self.recv_task(conn))
                send_task = ensure_future(self.send_task(conn))
                await asyncio.gather(recv_task, send_task)

        loop = asyncio.new_event_loop() if new_loop else asyncio.get_event_loop()
        loop.run_until_complete(_mainloop())
