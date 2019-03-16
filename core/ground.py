#!/usr/bin/python3
# -*- coding: utf-8 -*-
import enum
from asyncio import BaseEventLoop, new_event_loop
from threading import Thread
from typing import Union

from janus import Queue as _Queue


class Queue(_Queue):
    """可同时工作在协程和线程中的FIFO队列。"""

    def get(self, **kwargs):
        return self.sync_q.get(**kwargs)

    def put(self, item, **kwargs):
        self.sync_q.put(item, **kwargs)

    async def async_get(self):
        return await self.async_q.get()

    async def async_put(self, item):
        await self.async_q.put(item)


class BlackBox(Thread):
    """黑盒是核心包对外提供服务的方式。
    每一个黑盒都是一个独立的线程（不考虑子线程），并且在线程内部至少有一个事件循环（loop属性）；
    黑盒拥有recv_queue和send_queue两个属性，它们都是Queue类的对象，并被用作与外界交互的接口。
    在不承担计算密集型工作的情况下，现代CPU中可以处理的线程数相当之高，因此不用考虑线程过多的问题。
    """

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


class EnumMeta(enum.EnumMeta):
    def __call__(cls, item, *args, **kwargs):
        if isinstance(item, str) and item in cls:
            return super().__call__(cls[item], *args, **kwargs)
        return super().__call__(item, *args, **kwargs)

    def __contains__(cls, item):
        if isinstance(item, cls):
            return item._name_ in cls._member_map_
        elif isinstance(item, str):
            return item in cls._member_map_
        member_values = map(lambda x: x.value, cls._member_map_.values())
        return item in member_values


class Enum(enum.Enum, metaclass=EnumMeta):
    def __str__(self):
        return self.name
