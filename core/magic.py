#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from contextlib import suppress
from functools import wraps


def new_game_plus(func):
    # @formatter:off
    @wraps(func)
    def _new_game_plus(*args, **kwargs):
        while True:
            func(*args, **kwargs)
    # @formatter:on
    return _new_game_plus


def async_new_game_plus(func):
    # @formatter:off
    @wraps(func)
    async def _async_new_game_plus(*args, **kwargs):
        while True:
            await func(*args, **kwargs)
    # @formatter:on
    return _async_new_game_plus


def undead_curse(interval, callback, *exceptions):
    # @formatter:off
    def _undead_curse(func):
        @wraps(func)
        def __undead_curse(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    time.sleep(interval)
        return __undead_curse
    # @formatter:on
    return _undead_curse


def async_undead_curse(interval, callback, *exceptions):
    # @formatter:off
    def _async_undead_curse(func):
        @wraps(func)
        async def __async_undead_curse(*args, **kwargs):
            while True:
                try:
                    await func(*args, **kwargs)
                except exceptions as e:
                    callback(e)
                finally:
                    time.sleep(interval)
        return __async_undead_curse
    # @formatter:on
    return _async_undead_curse


def vow_of_silence(*exceptions):
    # @formatter:off
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
    def _async_vow_of_silence(func):
        @wraps(func)
        async def __async_vow_of_silence(*args, **kwargs):
            with suppress(exceptions):
                return await func(*args, **kwargs)
        return __async_vow_of_silence
    # @formatter:on
    return _async_vow_of_silence
