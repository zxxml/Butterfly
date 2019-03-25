#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ssl
import ujson
from threading import Thread

from dataclasses import dataclass

from butterfly import tricks
from butterfly.body import Body
from butterfly.eye import Eye
from butterfly.node import Node


@dataclass
class Slave:
    host: str
    port: int
    passwd: str
    width: int
    height: int
    v_flip: bool
    h_flip: bool
    quality: int
    com_port: str
    baud_rate: int
    ssl_ctx: ssl.SSLContext = None

    def __post_init__(self):
        self.eye_node = Node(self.host, self.port, self.passwd, 'slave_eye', 'master_eye', self.ssl_ctx)
        self.body_node = Node(self.host, self.port, self.passwd, 'slave_body', 'master_body', self.ssl_ctx)
        self.eye = Eye(self.width, self.height, self.v_flip, self.h_flip, self.quality)
        self.body = Body(self.com_port, self.baud_rate)

    def mainloop(self):
        # create and start all threads
        # modern computer is really powerful
        # and it's ok to run so many thread
        eye_thread = Thread(target=self.handle_eye)
        body_thread = Thread(target=self.handle_body)
        self.eye_node.start()
        self.body_node.start()
        self.eye.start()
        self.body.start()
        eye_thread.start()
        body_thread.start()

    @tricks.new_game_plus
    def handle_eye(self):
        width, height, img = self.eye.send_q.get()
        temp = base64.b64encode(img.tobytes())
        data = ujson.dumps((width, height, temp))
        self.eye_node.send_data(data)

    @tricks.new_game_plus
    def handle_body(self):
        data = self.body_node.recv_data()
        act, det = ujson.loads(data)
        temp = '{0} {1}\n'.format(act, det)
        self.body.recv_q.put(temp)


if __name__ == '__main__':
    slave = Slave('localhost', 8080, '123456', 800, 600, True, True, 60, 'COM4', 9600)
    slave.mainloop()
