#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ujson as json
from base64 import b64decode, b64encode
from enum import auto
from typing import Union

from dataclasses import dataclass

from ground import Enum


class Action(Enum):
    video = 0
    audio = auto()
    vehicle = auto()
    camera = auto()
    minigun = auto()

    def is_complex(self):
        return self in ('video', 'audio')

    def is_simple(self):
        return not self.is_complex()


@dataclass
class Packet:
    """分组是一个三元组，它包括action、detail和value三个部分。
    当需要构造一个分组时，可以直接使用分组的构造方法；
    当需要打包一个分组时，可以直接使用它的pack()方法；
    当需要解包一个分组时，可以使用报文的unpack(packet)方法；
    当需要解包一个分组的detail时，可以直接使用它的unpack_detail()方法。
    分组的具体内容如下所示：
    视频传输分组：video <width>x<height> <视频帧>
    音频传输分组：audio <sample_rate>x<channel_num> <音频帧>
    载具控制分组：vehicle vertical/horizontal <速度>
    摄像头控制分组：camera vertical/horizontal <速度>
    水弹枪控制分组：minigun vertical/horizontal/fire <速度>
    """
    action: Union[Action, str]
    detail: str
    value: Union[bytes, int]

    def __post_init__(self):
        self.action = Action(self.action)

    def __str__(self):
        if self.action.is_complex():
            return '{0} {1}'.format(self.action, self.detail)
        return '{0} {1} {2}'.format(self.action, self.detail, self.value)

    def __repr__(self):
        if self.action.is_complex():
            return '{0} {1}\n'.format(self.action, self.detail)
        return '{0} {1} {2}\n'.format(self.action, self.detail, self.value)

    def pack(self):
        action = str(self.action)
        value = b64encode(self.value) if self.action.is_complex() else self.value
        return json.dumps((action, self.detail, value))

    @staticmethod
    def unpack(packet):
        action, detail, value = json.loads(packet)
        value = b64decode(value) if Action(action).is_complex() else value
        return Packet(action, detail, value)

    def unpack_detail(self):
        if self.action.is_complex():
            return [int(each) for each in self.detail.split('x')]
        return self.detail
