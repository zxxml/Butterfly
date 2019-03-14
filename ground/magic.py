#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time


def new_game_plus(func):
    # @formatter:off
    def _new_game_plus(*args, **kwargs):
        while True:
            func(*args, **kwargs)
    # @formatter:on
    return _new_game_plus


def async_new_game_plus(func):
    # @formatter:off
    async def _async_new_game_plus(*args, **kwargs):
        while True:
            await func(*args, **kwargs)
    # @formatter:on
    return _async_new_game_plus


def undead_curse(interval, callback, *exceptions):
    # @formatter:off
    def _undead_curse(func):
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
