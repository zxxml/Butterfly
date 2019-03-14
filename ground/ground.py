#!/usr/bin/python3
# -*- coding: utf-8 -*-
from asyncio import BaseEventLoop, new_event_loop
from threading import Thread
from typing import Union

from janus import Queue as _Queue


class Queue(_Queue):
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
        self.loop: Union[BaseEventLoop, None] = None

    def run(self):
        self.loop = new_event_loop()
        self.recv_queue = Queue(maxsize=self.max_size, loop=self.loop)
        self.send_queue = Queue(maxsize=self.max_size, loop=self.loop)
