#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio

import janus
import websockets
from dataclasses import dataclass
from websockets import ConnectionClosed

from core import illusions
from network.bridge import Bridge
from network.keeper import Keeper
from network.packet import Packet


@dataclass
class Client:
    host: str
    port: int
    passwd: bytes
    type: str

    def __post_init__(self):
        self.url = Bridge.get_url(self.host, self.port, self.type)
        self.keeper = Keeper(self.passwd)
        # if you use Client in thread, after calling mainloop()
        # you shall check if recv_q or send_q is None
        self.recv_q: janus.Queue = None
        self.send_q: janus.Queue = None

    def mainloop(self):
        loop = asyncio.new_event_loop()
        self.recv_q = janus.Queue(loop=loop)
        self.send_q = janus.Queue(loop=loop)
        loop.run_until_complete(self.async_mainloop())

    @illusions.async_undead_curse(5, print, ConnectionClosed, OSError)
    async def async_mainloop(self):
        kwargs = {'extra_headers': Bridge.get_headers(self.passwd)}
        async with websockets.connect(self.url, **kwargs) as conn:
            recv_pkt = asyncio.ensure_future(self.recv_pkt(conn))
            send_pkt = asyncio.ensure_future(self.send_pkt(conn))
            await asyncio.gather(recv_pkt, send_pkt)

    def recv_content(self):
        return self.send_q.sync_q.get()

    def send_content(self, dest: str, content: bytes):
        self.send_q.sync_q.put((dest, content))

    @illusions.async_new_game_plus
    async def recv_pkt(self, conn):
        data = await conn.recv()
        temp = self.keeper.decrypt(data)
        pkt = Packet.from_bytes(temp)
        await self.recv_q.async_q.put(pkt.content)

    @illusions.async_new_game_plus
    async def send_pkt(self, conn):
        dest, content = await self.send_q.async_q.get()
        pkt = Packet(dest, content)
        temp = pkt.to_bytes()
        data = self.keeper.encrypt(temp)
        await conn.send(data)


if __name__ == '__main__':
    from threading import Thread
    from time import sleep

    client = Client('localhost', 8080, b'123456', 'default')
    Thread(target=client.mainloop).start()
    sleep(1)
    client.send_content('default', b'fuck')
    client.send_content('default', b'fuck')
    client.send_content('default', b'fuck')
    client.send_content('default', b'fuck')
    client.send_content('default', b'fuck')
