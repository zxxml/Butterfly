#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import ssl

import websockets
from websockets import ConnectionClosed

from butterfly import tricks
from butterfly.router import Router
from butterfly.utils import BlackBox


class Node(BlackBox):
    def __init__(self, host: str, port: int, passwd: str, type: str,
                 peer: str, ssl_ctx: ssl.SSLContext = None, **kwargs):
        super().__init__(**kwargs)
        self.url = Router.get_url(host, port, type, peer, ssl_ctx)
        self.headers = Router.get_headers(passwd)
        self.ssl_ctx = ssl_ctx

    def run(self):
        self.loop.run_until_complete(self.mainloop())

    def recv_data(self):
        return self.recv_q.get()

    def send_data(self, data):
        self.send_q.put(data)

    @tricks.async_undead_curse(2, print, ConnectionClosed, OSError)
    async def mainloop(self):
        kwargs = {'extra_headers': self.headers}
        async with websockets.connect(self.url, **kwargs) as conn:
            recv_data = asyncio.ensure_future(self.async_recv_data(conn))
            send_data = asyncio.ensure_future(self.async_send_data(conn))
            await asyncio.gather(recv_data, send_data)

    @tricks.async_new_game_plus
    async def async_recv_data(self, conn):
        data = await conn.recv()
        await self.recv_q.async_put(data)

    @tricks.async_new_game_plus
    async def async_send_data(self, conn):
        data = await self.send_q.async_get()
        await conn.send(data)


if __name__ == '__main__':
    # specify the same type and peer
    # and you'll get a simple echo program
    node = Node('localhost', 8080, '123456', 'echo', 'echo')
    node.start()
    node.send_data('hello')
    print(node.recv_data())
