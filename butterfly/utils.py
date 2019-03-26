#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import queue
import time
from threading import Thread

import janus

from butterfly import tricks


class Queue(janus.Queue):
    """Queue can work in both threads and coroutines.
    However, it can only work in one event loop
    which is `asyncio.get_event_loop()` by default.
    """

    def get(self, **kwargs):
        return self.sync_q.get(**kwargs)

    def put(self, item, **kwargs):
        self.sync_q.put(item, **kwargs)

    @tricks.vow_of_silence(queue.Empty)
    def get_anyway(self):
        return self.sync_q.get_nowait()

    @tricks.vow_of_silence(queue.Full)
    def put_anyway(self, item):
        self.sync_q.put_nowait(item)

    async def async_get(self):
        return await self.async_q.get()

    async def async_put(self, item):
        await self.async_q.put(item)


class BlackBox(Thread):
    """BlackBox is designed for this usage:
    you would like to create a standby thread
    so that you can send tasks to it through a queue
    and recv results from another queue meanwhile.
    But there may be coroutines in this thread
    and they are the real executors for your tasks
    which means they need to access to the two queues.
    BlackBox could handle the conflict for this purpose.
    """

    def __init__(self, max_size: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.loop = asyncio.new_event_loop()
        self.recv_q = Queue(maxsize=max_size, loop=self.loop)
        self.send_q = Queue(maxsize=max_size, loop=self.loop)

    @staticmethod
    @tricks.new_game_plus
    def hang_by():
        time.sleep(3600)
