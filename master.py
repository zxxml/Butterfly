#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread

import cv2
import numpy as np
import sounddevice as sd
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.widget import Widget

import config
from client import Client
from message import Message
from utiliy import PausableThread, SharedVariable, undead_curse


class MasterButton(Button, config.MasterButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.master = App.get_running_app().master
        self.shared_image = App.get_running_app().shared_image

    def on_touch_down(self, touch):
        if touch.is_triple_tap:
            self.disabled = not self.disabled
            self.opacity = 1 - self.opacity
        super().on_touch_down(touch)

    def on_press(self):
        if self.parent.name in ('left_stick', 'right_stick'):
            action = MasterButton.action_table[self.parent.name]
            detail = MasterButton.detail_table[self.name]
            self.on_stick_press(action, detail)
        elif self.parent.name == 'chirpy_chirps':
            self.on_chirpy_chirps_press()

    def on_stick_press(self, action, detail):
        msg = Message(action, detail, b'')
        self.master.send_queue.put(msg)

    def on_chirpy_chirps_press(self):
        if self.name == 'b_btn':
            self.master.record_audio_thread.resume()
        elif self.name == 'x_btn':
            self.save_image()
        elif self.name == 'y_btn':
            self.on_stick_release('vehicle')
            self.on_stick_release('camera')

    def on_release(self):
        if self.parent.name in ('left_stick', 'right_stick'):
            action = MasterButton.action_table[self.parent.name]
            self.on_stick_release(action)
        elif self.parent.name == 'chirpy_chirps':
            self.on_chirpy_chirps_release()

    def on_stick_release(self, action):
        msg = Message(action, 'stop', b'')
        self.master.send_queue.put(msg)

    def on_chirpy_chirps_release(self):
        if self.name == 'b_btn':
            self.master.record_audio_thread.pause()

    def save_image(self):
        if not self.shared_image:
            return None
        image = self.shared_image.get()[-1]
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        cv2.imwrite('{}.jpg'.format(now), image)


class MasterPanel(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas_group = InstructionGroup()
        self.ids.image.canvas.add(self.canvas_group)

    def update_image(self, width, height, image):
        factor = min(self.ids.image.width / width, self.ids.image.height / height)
        width, height = int(factor * width), int(factor * height)
        image = cv2.resize(image, (width, height))
        # noinspection PyArgumentList
        texture = Texture.create(size=(width, height), colorfmt='bgr')
        texture.flip_vertical()
        texture.flip_horizontal()
        texture.blit_buffer(image.tobytes(), colorfmt='bgr')
        self.ids.image.texture = texture


class MasterWindow(App, config.MasterWindow):
    Builder.load_file('master.kv')
    Window.size = (config.MasterWindow.width, config.MasterWindow.height)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.shared_image = SharedVariable()
        self.panel = MasterPanel()
        Clock.schedule_interval(self.update_image, MasterWindow.interval)

    def build(self):
        return self.panel

    def update_image(self, _):
        if not self.shared_image:
            return None
        return self.panel.update_image(*self.shared_image.get())


class Master(Client, config.Master):
    """主机是从机的上位机。
    主机将不间断地接收从机发送的摄像头回传报文，并显示在屏幕上。
    """

    def __init__(self, host, port, passwd, ssl_context=None):
        super().__init__(host, port, passwd, 'master', ssl_context)
        self.record_audio_thread = self.handle_record_audio_thread()
        self.window = MasterWindow(self)

    async def recv_task(self, conn):
        while True:
            msg = await conn.recv()
            msg = Message.unpack(msg)
            if msg.action == 'image':
                width, height = msg.unpack_detail()
                image = np.fromstring(msg.stream, np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                self.window.shared_image.put((width, height, image))

    def handle_mainloop_thread(self):
        mainloop_thread = Thread(target=super().mainloop, args=(True,))
        mainloop_thread.setDaemon(True)
        return mainloop_thread

    def handle_record_audio_thread(self):
        @undead_curse(Master.restart_interval, sd.PortAudioError)
        def _handle_record_audio_thread(signal):
            args = (Master.sampling_rate, Master.block_size)
            kwargs = {'channels': Master.channel_num}
            with sd.InputStream(*args, **kwargs) as input_stream:
                while True:
                    signal.wait()
                    audio = input_stream.read(Master.block_size)
                    msg = Message('speaker', Master.detail, audio[0].tobytes())
                    self.send_queue.put(msg)

        record_audio_thread = PausableThread(target=_handle_record_audio_thread)
        record_audio_thread.setDaemon(True)
        return record_audio_thread

    def mainloop(self, **kwargs):
        self.handle_mainloop_thread().start()
        self.record_audio_thread.start()
        self.window.run()


if __name__ == '__main__':
    test_master = Master('localhost', 8080, '123456')
    test_master.mainloop()
