#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import ensure_future
from collections import defaultdict
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import websockets
from websockets import ConnectionClosed

from config import ServerConfig, Status, Subtype
from ground import BlackBox, Queue
from magic import async_new_game_plus


class Server(BlackBox):
    def __init__(self, config: ServerConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.bridges = defaultdict(lambda: defaultdict(lambda: None))
        self.queues = defaultdict(lambda: defaultdict(lambda: None))

    def process_request(self):
        def _process_request(path, _):
            query = parse_qs(urlparse(path).query)
            # 如果客户端未提供密码或提供的密码不正确，返回UNAUTHORIZED状态码
            # SSL/TLS会加密除host以外的所有内容，因此把鉴权机制放在URL中是安全的
            passwd = query.get('passwd', [])
            if not passwd or passwd[0] != self.config.passwd:
                return HTTPStatus.UNAUTHORIZED, [], b''
            # 如果客户端的类型不在Status中
            # 或者如果客户端的子类型不在Subtype中
            # 返回NOT_FOUND状态码
            status = query.get('status', [''])[0]
            subtype = query.get('subtype', [''])[0]
            if status not in Status or subtype not in Subtype:
                return HTTPStatus.NOT_FOUND, [], b''
            # 如果客户端类型对应的连接已存在
            # 返回FORBIDDEN状态码
            if self.bridges[subtype][status] is not None:
                return HTTPStatus.FORBIDDEN, [], b''

        return _process_request

    def server_handler(self):
        async def _server_handler(socket, path):
            query = parse_qs(urlparse(path).query)
            status = query['status'][0]
            subtype = query['subtype'][0]
            self.bridges[subtype][status] = socket
            self.queues[subtype][status] = Queue()
            try:
                handle_recv_task = ensure_future(self.handle_recv_task(socket, status, subtype))
                handle_send_task = ensure_future(self.handle_send_task(socket, status, subtype))
                await asyncio.gather(handle_recv_task, handle_send_task)
            except ConnectionClosed:
                self.bridges[subtype][status] = None
                self.queues[subtype][status] = None

        return _server_handler

    @async_new_game_plus
    async def handle_recv_task(self, socket, status, subtype):
        msg = await socket.recv()
        opposite_status = str(-Status(status))
        opposite_queue = self.queues[subtype][opposite_status]
        if opposite_queue is None:
            return None
        await opposite_queue.async_put(msg)

    async def handle_send_task(self, socket, status, subtype):
        queue = self.queues[subtype][status]
        while True:
            item = await queue.async_get()
            await socket.send(item)

    def mainloop(self, **kwargs):
        kwargs.setdefault('host', self.config.host)
        kwargs.setdefault('port', self.config.port)
        kwargs.setdefault('ssl', self.config.ssl_context)
        kwargs.setdefault('loop', self.loop)
        kwargs.setdefault('process_request', self.process_request())
        start_server = websockets.serve(self.server_handler(), **kwargs)
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    def run(self):
        super().run()
        self.mainloop()
