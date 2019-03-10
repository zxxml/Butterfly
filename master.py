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

from client import Client
from config import Master as _Master
from config import MasterApp as _MasterApp
from config import MasterButton as _MasterButton
from message import Message
from utiliy import PausableThread, SharedVariable, undead_curse


class MasterButton(Button, _MasterButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_press(self):
        if self.parent.name in ('left_stick', 'right_stick'):
            action = MasterButton.action_table[self.parent.name]
            detail = MasterButton.detail_table[self.name]
            value = MasterButton.value_table[self.name]
            self.app.send_msg(action, detail, value)
        elif self.parent.name == 'chirpy_chirps':
            button_id = MasterButton.button_table[self.name]
            self.app.on_joy_button_down(None, None, button_id)

    def on_release(self):
        if self.parent.name in ('left_stick', 'right_stick'):
            action = MasterButton.action_table[self.parent.name]
            detail = MasterButton.detail_table[self.name]
            self.app.send_msg(action, detail, 0)
        elif self.parent.name == 'chirpy_chirps':
            button_id = MasterButton.button_table[self.name]
            self.app.on_joy_button_up(None, None, button_id)

    def on_touch_down(self, touch):
        if touch.is_triple_tap:
            self.disabled = not self.disabled
            self.opacity = 1 - self.opacity
        super().on_touch_down(touch)


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
        texture.blit_buffer(image.tobytes(), colorfmt='bgr')
        self.ids.image.texture = texture


class MasterApp(App, _MasterApp):
    Builder.load_file('master.kv')
    Window.size = (_MasterApp.width, _MasterApp.height)

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.master = master
        self.shared_image = SharedVariable()
        self.panel = MasterPanel()
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)

    def update_image(self, _interval):
        if not self.shared_image:
            return None
        return self.panel.update_image(*self.shared_image.get())

    def save_image(self):
        if not self.shared_image:
            return None
        image = self.shared_image.get()[-1]
        now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        cv2.imwrite('{}.jpg'.format(now), image)

    def send_msg(self, action, detail, value):
        msg = Message(action, detail, value)
        self.master.send_queue.put(msg)

    def build(self):
        return self.panel

    def run(self):
        Clock.schedule_interval(self.update_image, MasterApp.image_interval)
        super().run()

    def on_joy_axis(self, _win, _stick_id, axis_id, value):
        if axis_id in (0, 1, 3, 4):
            action = MasterApp.action_table[axis_id]
            detail = MasterApp.detail_table[axis_id]
            self.send_msg(action, detail, value)

    def on_joy_button_down(self, _win, _stick_id, button_id):
        if button_id == 1:
            self.master.record_audio_thread.resume()
        elif button_id == 2:
            self.save_image()
        elif button_id == 3:
            self.send_msg('vehicle', 'vertical', 0)
            self.send_msg('vehicle', 'horizontal', 0)
            self.send_msg('camera', 'vertical', 0)
            self.send_msg('camera', 'horizontal', 0)

    def on_joy_button_up(self, _win, _stick_id, button_id):
        if button_id == 1:
            self.master.record_audio_thread.pause()


class Master(Client, _Master):
    """主机是从机的上位机。
    主机将不间断地接收从机发送的摄像头回传报文，并显示在屏幕上。
    """

    def __init__(self, host, port, passwd, ssl_context=None):
        super().__init__(host, port, passwd, 'master', ssl_context)
        self.record_audio_thread = self.handle_record_audio_thread()
        self.window = MasterApp(self)

    async def recv_task(self, conn):
        while True:
            msg = await conn.recv()
            msg = Message.unpack(msg)
            if msg.action == 'image':
                width, height = msg.unpack_detail()
                image = np.fromstring(msg.value, np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                self.window.shared_image.put((width, height, image))

    def handle_mainloop_thread(self):
        mainloop_thread = Thread(target=super().mainloop, args=(True,))
        mainloop_thread.setDaemon(True)
        return mainloop_thread

    def handle_record_audio_thread(self):
        kwargs = {'samplerate': Master.sampling_rate, 'blocksize': Master.block_size, 'channels': Master.channel_num}
        detail = '{0}x{1}x{2}'.format(Master.sampling_rate, Master.block_size, Master.channel_num)

        @undead_curse(Master.restart_interval, sd.PortAudioError)
        def _handle_record_audio_thread(signal):
            with sd.InputStream(**kwargs) as input_stream:
                while True:
                    signal.wait()
                    audio = input_stream.read(Master.block_size)
                    msg = Message('speaker', detail, audio[0].tobytes())
                    self.send_queue.put(msg)

        record_audio_thread = PausableThread(target=_handle_record_audio_thread)
        record_audio_thread.setDaemon(True)
        return record_audio_thread

    def mainloop(self):
        self.handle_mainloop_thread().start()
        self.record_audio_thread.start()
        self.window.run()


if __name__ == '__main__':
    test_master = Master('localhost', 8080, '123456')
    test_master.mainloop()
