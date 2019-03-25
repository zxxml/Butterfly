#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ssl
import ujson
from threading import Thread

import cv2
import numpy as np
from kivy.app import App
from kivy.clock import mainthread
from kivy.core.image import Texture
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.widget import Widget

from butterfly import tricks
from butterfly.node import Node


class Master(App):
    def __init__(self, host: str, port: int, passwd: str,
                 ssl_ctx: ssl.SSLContext = None, **kwargs):
        super().__init__(**kwargs)
        self.window = MasterWin(self)
        self.eye_node = Node(host, port, passwd, 'master_eye', 'slave_eye', ssl_ctx)
        self.body_node = Node(host, port, passwd, 'master_body', 'slave_body', ssl_ctx)

    def mainloop(self):
        eye_thread = Thread(target=self.handle_eye)
        body_thread = Thread(target=self.handle_body)
        self.eye_node.setDaemon(True)
        self.body_node.setDaemon(True)
        eye_thread.setDaemon(True)
        body_thread.setDaemon(True)
        self.eye_node.start()
        self.body_node.start()
        eye_thread.start()
        body_thread.start()
        self.run()

    def build(self):
        return self.window

    @tricks.new_game_plus
    def handle_eye(self):
        data = self.eye_node.recv_data()
        width, height, temp = ujson.loads(data)
        print(width, height)
        temp = base64.b64decode(temp)
        img_jpg = np.fromstring(temp, np.uint8)
        img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)
        self.window.update_img(width, height, img)

    @tricks.new_game_plus
    def handle_body(self):
        pass


class MasterWin(Widget):
    Builder.load_file('master.kv')
    Window.size = (640, 480)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master

    @mainthread
    def update_img(self, width, height, img):
        texture = Texture.create(size=(width, height), colorfmt='bgr')
        texture.blit_buffer(img.tobytes(), colorfmt='bgr')
        self.ids.img.texture = texture


if __name__ == '__main__':
    master = Master('localhost', 8080, '123456')
    master.mainloop()
