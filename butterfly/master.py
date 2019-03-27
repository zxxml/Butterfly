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
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Line
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

from butterfly import tricks
from butterfly.ear import Ear
from butterfly.node import Node
from butterfly.sight import Sight


class Master(App):
    def __init__(self, host: str, port: int, passwd: str,
                 api_key: str, api_sec: str, spl_rate: int,
                 ch_num: int, ssl_ctx: ssl.SSLContext = None, **kwargs):
        super().__init__(**kwargs)
        self.window = MasterWin(self)
        self.eye_node = Node(host, port, passwd, 'master_eye', 'slave_eye', ssl_ctx)
        self.body_node = Node(host, port, passwd, 'master_body', 'slave_body', ssl_ctx)
        self.ear_node = Node(host, port, passwd, 'master_ear', 'slave_mouth', ssl_ctx)
        self.sight = Sight(api_key, api_sec)
        self.ear = Ear(spl_rate, ch_num)

    def mainloop(self):
        # create and start all threads
        # modern computer is really powerful
        # and it's ok to run so many thread
        eye_thread = Thread(target=self.handle_eye)
        sight_thread = Thread(target=self.handle_sight)
        ear_thread = Thread(target=self.handle_ear)
        # make sure to close all threads
        # after exiting the application
        self.eye_node.setDaemon(True)
        self.body_node.setDaemon(True)
        self.ear_node.setDaemon(True)
        self.sight.setDaemon(True)
        self.ear.setDaemon(True)
        eye_thread.setDaemon(True)
        sight_thread.setDaemon(True)
        ear_thread.setDaemon(True)
        self.eye_node.start()
        self.body_node.start()
        self.ear_node.start()
        self.sight.start()
        self.ear.start()
        eye_thread.start()
        sight_thread.start()
        ear_thread.start()
        self.run()

    @tricks.new_game_plus
    def handle_eye(self):
        data = self.eye_node.recv_data()
        width, height, temp = ujson.loads(data)
        temp = base64.b64decode(temp)
        img_jpg = np.fromstring(temp, np.uint8)
        img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)
        # update sight with JPEG encoded img
        # and update img with bitmap
        self.sight.recv_q.put_anyway((width, height, img_jpg))
        self.window.update_img(width, height, img)

    @tricks.new_game_plus
    def handle_sight(self):
        width, height, rects = self.sight.send_q.get()
        self.window.update_rects(width, height, rects)

    @tricks.new_game_plus
    def handle_ear(self):
        audio = self.ear.send_q.get()
        data = base64.b64encode(audio.tobytes())
        self.ear_node.send_data(data)

    def build(self):
        return self.window


class MasterWin(FloatLayout):
    Builder.load_file('master.kv')
    Window.size = (640, 480)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.rects = InstructionGroup()
        self.ids.mask.canvas.add(self.rects)
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)

    @mainthread
    def update_img(self, width, height, img):
        texture = Texture.create(size=(width, height))
        texture.blit_buffer(img.tobytes())
        texture.flip_vertical()
        texture.flip_horizontal()
        self.ids.img.texture = texture

    @mainthread
    def update_rects(self, width, height, rects):
        self.rects.clear()
        # since the img may be scaled
        # need to scale the mask as well
        size = self.ids.img.size
        scale = min(size[0] / width, size[1] / height)
        print(scale)
        # self.ids.mask.x_scale = scale
        # self.ids.mask.y_scale = scale
        self.ids.mask.size = (width * scale, height * scale)
        # self.ids.mask.center = self.center
        print(self.ids.mask.center, self.center, self.ids.mask.size, self.ids.mask.pos)
        size = self.ids.mask.size
        pos = self.ids.mask.pos
        for each in rects:
            # due to the img is flipped
            # the mask need to be flipped too
            each = [x for x in each]
            print(each)
            each = [x * scale for x in each]
            left = size[0] - each[0]
            top = size[1] - each[1]
            temp = (left + pos[0], top + pos[1], -each[2], -each[3])
            print(each, temp)
            # noinspection PyArgumentList
            rect = Line(rectangle=temp)
            self.rects.add(rect)

    def on_joy_axis(self, _win, _stick_id, axis_id, val):
        if axis_id in (0, 1, 3, 4):
            act = {0: 'mov', 1: 'mov', 3: 'obs', 4: 'obs'}[axis_id]
            det = {0: 'down', 1: 'right', 3: 'down', 4: 'right'}[axis_id]
            self.handle_body(act, det, val)

    def on_joy_button_down(self, _win, _stick_id, btn_id):
        if btn_id == 1:
            self.master.ear.enable = True
        elif btn_id == 2:
            now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.ids.img.export_to_png('{0}.png'.format(now))
        elif btn_id == 3:
            self.handle_body('mov', 'down', 0)
            self.handle_body('mov', 'right', 0)
            self.handle_body('obs', 'down', 0)
            self.handle_body('obs', 'right', 0)

    def on_joy_button_up(self, _win, _stick_id, btn_id):
        if btn_id == 1:
            self.master.ear.enable = False

    def handle_body(self, act, det, val):
        data = ujson.dumps((act, det, val))
        self.master.body_node.send_data(data)


if __name__ == '__main__':
    api_key = 'bA20twdRcbtD0yjyUPhZzeopq4jmIOAH'
    api_sec = '83kb7C4P7MAUBpH8SkX-idR5q2z_fiby'
    master = Master('localhost', 8080, '123456',
                    api_key, api_sec, 44100, 2)
    master.mainloop()
