#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import base64
from http import HTTPStatus
from urllib import parse

import websockets
from dataclasses import dataclass
from websockets import ConnectionClosed

from core import illusions
from network.keeper import Keeper
from network.packet import Packet


@dataclass
class Bridge:
    host: str
    port: int
    passwd: bytes

    @staticmethod
    def get_url(host: str, port: int, type: str):
        tmpl = 'ws://{0}:{1}/?type={2}'
        return tmpl.format(host, port, type)

    @staticmethod
    def get_headers(passwd: bytes):
        # use headers to post passwd
        # since passwd may be really long
        # and url can not contain it
        keeper = Keeper(passwd)
        temp = keeper.encrypt(passwd)
        temp = base64.b64encode(temp)
        return {'passwd': temp.decode('utf-8')}

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.keeper = Keeper(self.passwd)
        self.queues = dict()

    def mainloop(self):
        kwargs = {'host': self.host, 'port': self.port, 'compression': None,
                  'process_request': self.process_req()}
        start_server = websockets.serve(self.server_handler(), **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()

    def process_req(self):
        def _process_req(path, headers):
            # reject if passwd is wrong
            # and return 401 status code
            passwd = self.get_passwd(headers)
            if passwd != self.passwd:
                return HTTPStatus.UNAUTHORIZED, [], b''
            # reject if conn already exists
            # and return 403 status code
            type = self.get_type(path)
            if type in self.queues:
                return HTTPStatus.FORBIDDEN, [], b''

        return _process_req

    def get_passwd(self, headers):
        # return None if no passwd or wrong passwd
        dirty = headers._dict.get('passwd', [''])[0]
        temp = dirty.encode('utf-8')
        temp = base64.b64decode(temp)
        return self.keeper.decrypt(temp)

    @staticmethod
    def get_type(path):
        # type is 'default' by default
        query = parse.parse_qs(parse.urlparse(path).query)
        return query.get('type', ['default'])[0]

    def server_handler(self):
        @illusions.async_vow_of_silence(ConnectionClosed, TypeError)
        async def _server_handler(conn, path):
            type = self.get_type(path)
            self.queues[type] = asyncio.Queue()
            try:
                recv_pkt = asyncio.ensure_future(self.recv_pkt(conn))
                send_pkt = asyncio.ensure_future(self.send_pkt(type, conn))
                await asyncio.gather(recv_pkt, send_pkt)
            finally:
                # clean up and return
                del self.queues[type]

        return _server_handler

    @illusions.async_new_game_plus
    async def recv_pkt(self, conn):
        data = await conn.recv()
        temp = self.keeper.decrypt(data)
        pkt = Packet.from_bytes(temp)
        if pkt.dest in self.queues:
            # leave the data for the dest conn
            # the dest conn shall hold its data
            await self.queues[pkt.dest].put(data)

    @illusions.async_new_game_plus
    async def send_pkt(self, type, conn):
        # a conn holds its own queue
        data = await self.queues[type].get()
        await conn.send(data)


if __name__ == '__main__':
    bridge = Bridge('localhost', 8080, b'123456')
    bridge.mainloop()
