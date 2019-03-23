#!/usr/bin/python3
# -*- coding: utf-8 -*-
from asyncio import ensure_future, gather
from collections import defaultdict
from http import HTTPStatus
from ssl import SSLContext
from urllib.parse import parse_qs, urlparse

from dataclasses import asdict, dataclass
from websockets import ConnectionClosed, serve as websockets_serve
 
from core.client import ClientConfig, Status, Subtype
from core.ground import BlackBox, Queue
from core.magic import async_new_game_plus


@dataclass
class ServerConfig:
    host: str
    port: int
    passwd: str
    ssl_context: SSLContext = None

    def __post_init__(self):
        self.host = str(self.host)
        self.port = int(self.port)
        self.passwd = str(self.passwd)

    def to_client_config(self, status, subtype):
        return ClientConfig(status=status, subtype=subtype, **asdict(self))


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
                recv_task = ensure_future(self.recv_task(socket, status, subtype))
                send_task = ensure_future(self.send_task(socket, status, subtype))
                await gather(recv_task, send_task)
            except ConnectionClosed:
                self.bridges[subtype][status] = None
                self.queues[subtype][status] = None

        return _server_handler

    @async_new_game_plus
    async def recv_task(self, socket, status, subtype):
        msg = await socket.recv()
        opposite_status = str(-Status(status))
        opposite_queue = self.queues[subtype][opposite_status]
        if opposite_queue is None:
            return None
        await opposite_queue.async_put(msg)

    async def send_task(self, socket, status, subtype):
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
        start_server = websockets_serve(self.server_handler(), **kwargs)
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()


if __name__ == '__main__':
    test_config = ServerConfig('localhost', 8080, '123456')
    test_server = Server(test_config)
    test_server.start()
