#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from threading import Event, Thread


class SharedVariable:
    """写者优先的共享变量。"""

    def __init__(self, x=None):
        from readerwriterlock import rwlock
        self.lock = rwlock.RWLockWrite()
        self.value = x

    def __bool__(self):
        with self.lock.gen_rlock():
            return self.value is not None

    def get(self):
        with self.lock.gen_rlock():
            return self.value

    def put(self, x):
        with self.lock.gen_wlock():
            self.value = x


class PausableThread(Thread):
    """可暂停的线程，它在初始化后是暂停的。
    它的target的第一个参数应当是signal，当允许暂停时调用signal.wait()方法。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signal = Event()
        self._args = (self.signal, *self._args)

    def pause(self):
        self.signal.clear()

    def resume(self):
        self.signal.set()


def undead_curse(interval, *exceptions):
    """肉体是脆弱的，死亡来得如此突然。但灵魂是如此的坚强，渴望生存的意志是如此的不朽。
    换言之，虽然人不能永生，对死亡心存畏惧才让人们不死。失去这一点，人性将难以维持。
    如果你又倒下了，请再次站起来，这就是不死人的悲歌。
    """

    # @formatter:off
    def _undead_curse(func):
        def __undead_curse(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except exceptions as e:
                    print(e)
                finally:
                    time.sleep(interval)
        return __undead_curse
    # @formatter:on
    return _undead_curse
