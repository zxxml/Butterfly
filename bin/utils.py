#!/usr/bin/python3
# -*- coding: utf-8 -*-
import signal


def is_any_none(*items):
    items = map(lambda x: x is None, items)
    return any(items)


def is_all_none(*items):
    items = map(lambda x: x is None, items)
    return all(items)


def fix_signal():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
