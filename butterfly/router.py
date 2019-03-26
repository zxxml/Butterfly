#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import ssl
from http import HTTPStatus
from urllib import parse

import websockets
from dataclasses import dataclass
from websockets import ConnectionClosed
from websockets.http import Headers

from butterfly import tricks


@dataclass
class Router:
    """Router is a router in application layer, transferring data.
    A node connects the router with its own type and peer by websocket,
    and the router will transfer its data to the peer node if it exists.
    Router is not designed to work in sub-thread, please don't try it.
    """
    host: str
    port: int
    passwd: str
    ssl_ctx: ssl.SSLContext = None

    @staticmethod
    def get_url(host: str, port: int, type: str,
                peer: str, ssl_ctx: ssl.SSLContext):
        proto = 'ws' if ssl_ctx is None else 'wss'
        tmpl = '{}://{}:{}/?type={}&peer={}'
        return tmpl.format(proto, host, port, type, peer)

    @staticmethod
    def get_headers(passwd: str):
        # passwd may be really long
        # so that url cannot contain it
        # put it in headers is a better way
        return {'passwd': passwd}

    def __post_init__(self):
        self.send_qs = dict()

    def mainloop(self):
        kwargs = {'host': self.host, 'port': self.port,
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
            # reject if type is wrong
            # and return 403 status code
            type = self.get_type(path)
            if type in self.send_qs:
                return HTTPStatus.FORBIDDEN, [], b''

        return _process_req

    def server_handler(self):
        async def _server_handler(conn, path):
            type = self.get_type(path)
            peer = self.get_peer(path)
            self.send_qs[type] = asyncio.Queue()
            recv_data = asyncio.ensure_future(self.recv_data(conn, peer))
            send_data = asyncio.ensure_future(self.send_data(conn, type))
            try:
                await asyncio.gather(recv_data, send_data)
            except ConnectionClosed:
                # some tasks may be still pending
                # cancel them all to avoid error
                recv_data.cancel()
                send_data.cancel()
            finally:
                # no matter succeed or failed
                # clean up traces and return
                del self.send_qs[type]

        return _server_handler

    @tricks.async_new_game_plus
    async def recv_data(self, conn, peer):
        data = await conn.recv()
        if peer in self.send_qs:
            await self.send_qs[peer].put(data)

    @tricks.async_new_game_plus
    async def send_data(self, conn, type):
        data = await self.send_qs[type].get()
        await conn.send(data)

    @staticmethod
    def get_passwd(headers: Headers):
        # passwd is '' if not given
        dirty = headers._dict
        return dirty.get('passwd', [''])[0]

    @staticmethod
    def get_type(path: str):
        # type is '' if not given
        query = parse.urlparse(path).query
        temp = parse.parse_qs(query)
        return temp.get('type', [''])[0]

    @staticmethod
    def get_peer(path: str):
        # peer is '' if not given
        query = parse.urlparse(path).query
        temp = parse.parse_qs(query)
        return temp.get('peer', [''])[0]


if __name__ == '__main__':
    router = Router('0.0.0.0', 8080, '123456')
    router.mainloop()
