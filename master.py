#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread

import numpy as np
from cv2 import IMREAD_COLOR, imdecode
from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.widget import Widget

from core.client import Client
from core.magic import new_game_plus
from core.server import ServerConfig
from packet import Packet


class MasterWidget(Widget):
    Builder.load_file('master.kv')
    Window.size = (640, 480)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enable_minigun = False
        self.recv_queue = App.get_running_app().video_client.recv_queue
        self.send_queue = App.get_running_app().normal_client.send_queue
        Thread(target=self.handle_video, daemon=True).start()
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)

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

    def send_packet(self, action, detail, value):
        packet = Packet(action, detail, value)
        self.send_queue.put(packet.pack())

    def on_joy_axis(self, _win, _stick_id, axis_id, value):
        action_id = {0: 0, 1: 0, 3: 3, 4: 3, 2: 2, 5: 2}[axis_id]
        detail_id = {0: 0, 1: 1, 3: 0, 4: 1, 2: 2, 5: 2}[axis_id]
        action = {0: 'vehicle', 3: 'camera', 2: 'minigun'}[action_id]
        detail = {0: 'vertical', 1: 'horizontal', 2: 'fire'}[detail_id]
        action = 'minigun' if self.enable_minigun and action == 'vehicle' else action
        self.send_packet(action, detail, value)

    def on_joy_button_down(self, _win, _stick_id, button_id):
        if button_id == 0:
            self.enable_minigun = True
        elif button_id == 2:
            now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            self.ids.video.export_to_png('{0}.png'.format(now))
        elif button_id == 3:
            self.send_packet('vehicle', 'vertical', 0)
            self.send_packet('vehicle', 'horizontal', 0)
            self.send_packet('camera', 'vertical', 0)
            self.send_packet('camera', 'horizontal', 0)

    def on_joy_button_up(self, _win, _stick_id, button_id):
        if button_id == 0:
            self.enable_minigun = False


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
