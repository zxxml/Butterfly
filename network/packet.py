#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ujson

from dataclasses import dataclass


@dataclass
class Packet:
    dest: str
    content: bytes

    @staticmethod
    def from_bytes(data: bytes):
        data = base64.b64decode(data)
        temp = data.decode('utf-8')
        return Packet(**ujson.loads(temp))

    def to_bytes(self):
        data = ujson.dumps(self)
        temp = data.encode('utf-8')
        return base64.b64encode(temp)

    @staticmethod
    def unpack(data: bytes):
        return Packet.from_bytes(data)

    def pack(self):
        return self.to_bytes()
