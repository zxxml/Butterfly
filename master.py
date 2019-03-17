#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread

import numpy as np
from cv2 import IMREAD_COLOR, imdecode
from kivy.app import App
from kivy.clock import mainthread
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.widget import Widget

from client import Client
from magic import new_game_plus
from packet import Packet
from server import ServerConfig


class MasterWidget(Widget):
    Builder.load_file('master.kv')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recv_queue = App.get_running_app().video_client.recv_queue
        Thread(target=self.handle_video, daemon=True).start()

    @new_game_plus
    def handle_video(self):
        packet = self.recv_queue.get()
        packet = Packet.unpack(packet)
        image = np.fromstring(packet.value, np.uint8)
        image = imdecode(image, IMREAD_COLOR)
        self.update_image(packet.unpack_detail(), image)

    @mainthread
    def update_image(self, size, image):
        # noinspection PyArgumentList
        texture = Texture.create(size=size, colorfmt='bgr')
        texture.blit_buffer(image.tobytes(), colorfmt='bgr')
        self.ids.video.texture = texture


class Master(App):
    def __init__(self, server_config: ServerConfig, **kwargs):
        super().__init__(**kwargs)
        normal_config = server_config.to_client_config('master', 'normal')
        video_config = server_config.to_client_config('master', 'video')
        self.normal_client = Client(normal_config, daemon=True)
        self.video_client = Client(video_config, daemon=True)

    def build(self):
        return MasterWidget()

    def mainloop(self):
        self.normal_client.start()
        self.video_client.start()
        self.run()


if __name__ == '__main__':
    test_server_config = ServerConfig('localhost', 8080, '123456')
    test_master = Master(test_server_config)
    test_master.mainloop()
