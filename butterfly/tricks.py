#!/usr/bin/python3
# -*- coding: utf-8 -*-
# disable automatic formatter
import functools
import time
from contextlib import suppress


def new_game_plus(func):
    @functools.wraps(func)
    def _new_game_plus(*args, **kwargs):
        while True:
            func(*args, **kwargs)
    return _new_game_plus


def async_new_game_plus(func):
    @functools.wraps(func)
    async def _async_new_game_plus(*args, **kwargs):
        while True:
            await func(*args, **kwargs)
    return _async_new_game_plus


def undead_curse(intvl: float, callback, *exceptions):
    def _undead_curse(func):
        @functools.wraps(func)
        def __undead_curse(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    time.sleep(intvl)
        return __undead_curse
    return _undead_curse


def async_undead_curse(intvl: float, callback, *exceptions):
    def _async_undead_curse(func):
        @functools.wraps(func)
        async def __async_undead_curse(*args, **kwargs):
            while True:
                try:
                    await func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    time.sleep(intvl)
        return __async_undead_curse
    return _async_undead_curse


def vow_of_silence(*exceptions):
    def _vow_of_silence(func):
        @functools.wraps(func)
        def __vow_of_silence(*args, **kwargs):
            with suppress(exceptions):
                return func(*args, **kwargs)
        return __vow_of_silence
    return _vow_of_silence


def async_vow_of_silence(*exceptions):
    def _async_vow_of_silence(func):
        @functools.wraps(func)
        async def __async_vow_of_silence(*args, **kwargs):
            with suppress(exceptions):
                return await func(*args, **kwargs)
        return __async_vow_of_silence
    return _async_vow_of_silence
