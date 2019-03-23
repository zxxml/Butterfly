#!/usr/bin/python3
# -*- coding: utf-8 -*-
from asyncio import new_event_loop
from enum import Enum as enum_Enum
from enum import EnumMeta as enum_EnumMeta
from threading import Thread

from janus import Queue as janus_Queue


class Queue(janus_Queue):
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
    每个黑盒都是一个独立的线程（不考虑子线程），并且在线程内部至少有一个事件循环（loop属性）；
    黑盒拥有recv_queue和send_queue两个属性，它们都是Queue类的对象，并被用作与外界交互的接口。
    在不承担计算密集型工作的情况下，现代CPU中可以处理的线程数相当多，因此不用考虑线程过多的问题。
    """

    def __init__(self, max_size=0, **kwargs):
        super().__init__(**kwargs)
        self.max_size = max_size
        self.loop = new_event_loop()
        self.recv_queue = Queue(maxsize=self.max_size, loop=self.loop)
        self.send_queue = Queue(maxsize=self.max_size, loop=self.loop)

    def mainloop(self, **kwargs):
        pass

    def run(self):
        self.mainloop()


class EnumMeta(enum_EnumMeta):
    """将name与value同等对待的枚举元类。"""

    def __call__(cls, value, *args, **kwargs):
        if isinstance(value, str) and value in cls:
            return super().__call__(cls[value], *args, **kwargs)
        return super().__call__(value, *args, **kwargs)

    def __contains__(cls, value):
        if isinstance(value, cls):
            return value.name in cls._member_map_
        elif isinstance(value, str):
            return value in cls._member_map_
        member_values = map(lambda x: x.value, cls._member_map_.values())
        return value in member_values


class Enum(enum_Enum, metaclass=EnumMeta):
    """将name与value同等对待的枚举类。"""

    def __str__(self):
        return self.name

    def __eq__(self, value):
        if isinstance(value, Enum):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        return self.value == value
