#!/usr/bin/python3
# -*- coding: utf-8 -*-
from contextlib import suppress
from functools import wraps
from time import sleep as block_sleep


def new_game_plus(func):
    # @formatter:off
    """使命永无止境，轮回永无止境；现世中你永远地合上了双眼，来世里你仍要负重前行。
    不同的是，你或许更加强大，更加老练；随之而来的，你的使命也愈发困难，愈发沉重。
    """
    @wraps(func)
    def _new_game_plus(*args, **kwargs):
        while True:
            func(*args, **kwargs)
    # @formatter:on
    return _new_game_plus


def async_new_game_plus(func):
    # @formatter:off
    """千千万万个世界里，千千万万个你都在经历着无尽的轮回。
    有时你们的世界交织到一起，你们的任务捆绑在一起，但这不过是昙花一现罢了。
    """
    @wraps(func)
    async def _async_new_game_plus(*args, **kwargs):
        while True:
            await func(*args, **kwargs)
    # @formatter:on
    return _async_new_game_plus


def undead_curse(interval, callback, *exceptions):
    # @formatter:off
    """不死人的悲哀来自于他们无法逃避，无法逃避死亡，无法逃避宿命。
    而这悲哀的源头就是与火之时代一同诞生的不死诅咒，不死诅咒赋予了不死人在篝火处复活的能力；
    随着一次次的复活，不死人的神智逐渐涣散，为了维持终将逝去的理智，他们向篝火献上珍贵的人性。
    """
    def _undead_curse(func):
        @wraps(func)
        def __undead_curse(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    block_sleep(interval)
        return __undead_curse
    # @formatter:on
    return _undead_curse


def async_undead_curse(interval, callback, *exceptions):
    # @formatter:off
    """不同的世界里，不同的不死人都拥有相同的命运，他们的胸口也都烙印着相同的不死诅咒。"""
    def _async_undead_curse(func):
        @wraps(func)
        async def __async_undead_curse(*args, **kwargs):
            while True:
                try:
                    await func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    block_sleep(interval)
        return __async_undead_curse
    # @formatter:on
    return _async_undead_curse


def vow_of_silence(*exceptions):
    # @formatter:off
    """相传沉默禁令是黑发魔女蓓尔佳流传下来的秘法，在其有效范围内，将无法使用一切魔法。
    既然禁令范围内无法吟唱的话，想必发出呼救声也是不可能的吧。
    """
    def _vow_of_silence(func):
        @wraps(func)
        def __vow_of_silence(*args, **kwargs):
            with suppress(exceptions):
                return func(*args, **kwargs)
        return __vow_of_silence
    # @formatter:on
    return _vow_of_silence


def async_vow_of_silence(*exceptions):
    # @formatter:off
    """古往今来，蓓尔佳的追随者也分散在各个世界，提供着赎罪的机会。
    但既然赎罪者无法发出声音的话，赎罪的流程究竟是怎样的呢？
    """
    def _async_vow_of_silence(func):
        @wraps(func)
        async def __async_vow_of_silence(*args, **kwargs):
            with suppress(exceptions):
                return await func(*args, **kwargs)
        return __async_vow_of_silence
    # @formatter:on
    return _async_vow_of_silence
