#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ujson as json

import janus
from dataclasses import dataclass


@dataclass
class Message:
    """报文是一种三元组，它包括action、detail和stream（Base64编码）三个部分。
    当需要构造一个报文时，可以直接使用报文的构造方法；
    当需要打包一个报文时，可以直接使用它的pack()方法；
    当需要解包一个报文时，可以使用报文的unpack(msg)方法，唯一的参数是待解包的数据；
    当需要解包一个报文的detail时，可以直接使用它的unpack_detail()方法。
    报文的内容如下所示：
    测试报文：test ping/pong ping/pong
    摄像头回传报文：image 分辨率（形如640x480） 视频帧
    麦克风回传报文：audio return 音频帧
    载具控制报文：vehicle up/down/left/right 空
    摄像头控制报文：camera up/down/left/right 空
    扬声器控制报文：speaker 采样率x块大小x通道数 音频帧
    水弹枪控制报文：minigun
    """
    action: str
    detail: str
    stream: bytes

    def __str__(self):
        return '{} {}'.format(self.action, self.detail)

    def __repr__(self):
        return '{} {}\n'.format(self.action, self.detail)

    def pack(self):
        stream = base64.b64encode(self.stream)
        return json.dumps((self.action, self.detail, stream))

    @staticmethod
    def unpack(msg):
        action, detail, stream = json.loads(msg)
        stream = base64.b64decode(stream)
        return Message(action, detail, stream)

    def unpack_detail(self):
        """当需要扩展报文时，请保证unpack_detail()方法的有效性。"""
        return (int(each) for each in self.detail.split('x'))


class MessageQueue(janus.Queue):
    """可以同时工作在协程和线程中的FIFO队列。
    以插入数据为例，当需要在协程中使用它时，可以直接使用它的async_get()方法；
    当需要在线程中使用它时，可以直接使用它的get()方法。
    """

    async def async_get(self):
        return await self.async_q.get()

    async def async_put(self, x):
        return await self.async_q.put(x)

    def get(self, **kwargs):
        return self.sync_q.get(**kwargs)

    def put(self, x, **kwargs):
        return self.sync_q.put(x, **kwargs)


if __name__ == '__main__':
    test_msg = Message('test', 'ping', b'ping')
    print(test_msg.pack())
    print(Message.unpack(test_msg.pack()))
