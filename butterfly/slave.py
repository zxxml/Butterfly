#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ssl
import ujson
from threading import Thread

import numpy as np
from dataclasses import dataclass

from butterfly import tricks
from butterfly.body import Body
from butterfly.eye import Eye
from butterfly.mouth import Mouth
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
    spl_rate: int
    ch_num: int
    ssl_ctx: ssl.SSLContext = None

    def __post_init__(self):
        self.eye_node = Node(self.host, self.port, self.passwd, 'slave_eye', 'master_eye', self.ssl_ctx)
        self.body_node = Node(self.host, self.port, self.passwd, 'slave_body', 'master_body', self.ssl_ctx)
        self.mouth_node = Node(self.host, self.port, self.passwd, 'slave_mouth', 'master_ear', self.ssl_ctx)
        self.eye = Eye(self.width, self.height, self.v_flip, self.h_flip, self.quality)
        self.body = Body(self.com_port, self.baud_rate)
        self.mouth = Mouth(self.spl_rate, self.ch_num)

    def mainloop(self):
        # create and start all threads
        # modern computer is really powerful
        # and it's ok to run so many thread
        eye_thread = Thread(target=self.handle_eye)
        body_thread = Thread(target=self.handle_body)
        mouth_thread = Thread(target=self.handle_mouth)
        # make sure to close all threads
        # after exiting the application
        self.eye_node.setDaemon(True)
        self.body_node.setDaemon(True)
        self.mouth_node.setDaemon(True)
        self.eye.setDaemon(True)
        self.body.setDaemon(True)
        self.mouth.setDaemon(True)
        eye_thread.setDaemon(True)
        body_thread.setDaemon(True)
        mouth_thread.setDaemon(True)
        self.eye_node.start()
        self.body_node.start()
        self.mouth_node.start()
        self.eye.start()
        self.body.start()
        self.mouth.start()
        eye_thread.start()
        body_thread.start()
        mouth_thread.start()
        self.run()

    @tricks.new_game_plus
    def handle_eye(self):
        width, height, img = self.eye.send_q.get()
        temp = base64.b64encode(img.tobytes())
        data = ujson.dumps((width, height, temp))
        self.eye_node.send_data(data)

    @tricks.new_game_plus
    def handle_body(self):
        data = self.body_node.recv_data()
        act, det, val = ujson.loads(data)
        temp = '{0} {1} {2}\n'.format(act, det, val)
        self.body.recv_q.put(temp)

    @tricks.new_game_plus
    def handle_mouth(self):
        data = self.mouth_node.recv_data()
        temp = base64.b64decode(data)
        temp = np.fromstring(temp, np.float32)
        # make sure the shape is correct
        audio = temp.reshape((-1, self.ch_num))
        self.mouth.recv_q.put(audio)

    @staticmethod
    @tricks.vow_of_silence(KeyboardInterrupt)
    @tricks.new_game_plus
    def run():
        # since this is a multithreading program,
        # need to wait for KeyboardInterrupt manually
        pass


if __name__ == '__main__':
    slave = Slave('localhost', 8080, '123456', 640, 480,
                  True, True, 60, 'COM4', 9600, 44100, 2)
    slave.mainloop()
