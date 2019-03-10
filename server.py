#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import ensure_future
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import websockets
from websockets import ConnectionClosed

from config import Server as _Server
from message import MessageQueue


class Server(_Server):
    """（中转）服务器只负责端到端的报文中转。
    主机和从机可以单独地连接到服务器，地址格式为ws(s)://<host>:<port>/?passwd=<passwd>&client_type=<client_type>。
    以主机为例，当主机连接到服务器后，它便独占主机位，服务器将拒绝其他客户端以主机身份发起连接；
    主机可以向服务器发送报文，如果从机也已经连接到服务器，该报文将被转发给从机，反之该报文将被丢弃。
    服务器保证以下情况的鲁棒性：当客户端传入的参数不合法时；当多个相同类型的客户端依次发起连接时；当客户端断开连接时。
    """

    def __init__(self, host, port, passwd, ssl_context=None):
        self.host, self.port = host, port
        self.passwd = str(passwd)
        self.ssl_context = ssl_context
        self.clients = {'master': None, 'slave': None}
        self.send_queues = {'master': None, 'slave': None}

    def process_request(self):
        def _process_request(path, _):
            query = parse_qs(urlparse(path).query)
            # 如果客户端未提供密码或提供的密码不正确，返回401状态码
            # SSL/TLS会加密除host以外的所有内容，因此把鉴权机制放在URL中是安全的
            passwd = query.get('passwd', [])
            if not passwd or passwd[0] != self.passwd:
                return HTTPStatus.UNAUTHORIZED, [], b''
            # 如果客户端类型既不是master也不是slave，返回404状态码
            client_type = query.get('client_type', ['unknown'])[0]
            if client_type not in Server.chart:
                return HTTPStatus.NOT_FOUND, [], b''
            # 如果客户端类型对应的连接已存在，返回403状态码
            if self.clients[client_type] is not None:
                return HTTPStatus.FORBIDDEN, [], b''

        return _process_request

    def server_handler(self):
        async def _server_handler(conn, path):
            query = parse_qs(urlparse(path).query)
            client_type = query['client_type'][0]
            self.clients[client_type] = conn
            # noinspection PyTypeChecker
            self.send_queues[client_type] = MessageQueue()
            try:
                dst_client_type = Server.chart[client_type]
                recv_task = ensure_future(self.recv_task(conn, dst_client_type))
                send_task = ensure_future(self.send_task(conn, client_type))
                await asyncio.gather(recv_task, send_task)
            except ConnectionClosed:
                self.clients[client_type] = None
                self.send_queues[client_type] = None

        return _server_handler

    async def recv_task(self, conn, dst_client_type):
        while True:
            msg = await conn.recv()
            dst_send_queue = self.send_queues[dst_client_type]
            if dst_send_queue is None:
                continue
            await dst_send_queue.async_put(msg)

    async def send_task(self, conn, client_type):
        send_queue = self.send_queues[client_type]
        while True:
            msg = await send_queue.async_get()
            await conn.send(msg)

    def mainloop(self, new_loop=False, **kwargs):
        kwargs.setdefault('ssl', self.ssl_context)
        kwargs.setdefault('process_request', self.process_request())
        start_server = websockets.serve(self.server_handler(), self.host, self.port, **kwargs)
        loop = asyncio.new_event_loop() if new_loop else asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()


if __name__ == '__main__':
    test_server = Server('localhost', 8080, '123456')
    test_server.mainloop()
