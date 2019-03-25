#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ssl
import ujson
from datetime import datetime
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
        temp = base64.b64decode(temp)
        img_jpg = np.fromstring(temp, np.uint8)
        img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)
        self.window.update_img(width, height, img)

    def handle_body(self):
        pass


class MasterWin(Widget):
    Builder.load_file('master.kv')
    Window.size = (640, 480)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)

    @mainthread
    def update_img(self, width, height, img):
        texture = Texture.create(size=(width, height), colorfmt='bgr')
        texture.blit_buffer(img.tobytes(), colorfmt='bgr')
        self.ids.img.texture = texture

    def on_joy_axis(self, _win, _stick_id, axis_id, val):
        act = {0: 'mov', 1: 'mov', 3: 'obs', 4: 'obs'}[axis_id]
        det = {0: 'down', 1: 'right', 3: 'down', 4: 'right'}[axis_id]
        self.handle_body(act, det, val)

    def on_joy_button_down(self, _win, _stick_id, button_id):
        if button_id == 2:
            now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.ids.img.export_to_png('{0}.png'.format(now))
        elif button_id == 3:
            self.handle_body('mov', 'down', 0)
            self.handle_body('mov', 'right', 0)
            self.handle_body('obs', 'down', 0)
            self.handle_body('obs', 'right', 0)

    def on_joy_button_up(self, _win, _stick_id, button_id):
        pass

    def handle_body(self, act, det, val):
        data = ujson.dumps((act, det, val))
        self.master.body_node.send_data(data)


if __name__ == '__main__':
    master = Master('localhost', 8080, '123456')
    master.mainloop()
