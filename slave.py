#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from threading import Thread

import cv2
import numpy as np
import sounddevice as sd

import config
from client import Client
from message import Message, MessageQueue
from utiliy import undead_curse


class Slave(Client, config.Slave):
    """从机是载具控制器的上位机。
    从机将不间断地向服务器发送摄像头回传报文。
    从机接收到载具控制报文或摄像头控制报文时，该报文将被转发给载具控制器。
    从机接收到扬声器控制报文时，将播放该报文中的音频帧，暂时只能处理第一个扬声器控制报文中的detail。
    """

    def __init__(self, host, port, passwd, ssl_context=None):
        super().__init__(host, port, passwd, 'slave', ssl_context)
        self.serial_queue = MessageQueue()
        self.audio_queue = MessageQueue()

    async def recv_task(self, conn):
        while True:
            msg = await conn.recv()
            msg = Message.unpack(msg)
            if msg.action in ('vehicle', 'camera'):
                self.serial_queue.put(msg)
            elif msg.action == 'speaker':
                self.audio_queue.put(msg)

    def handle_image_thread(self):
        @undead_curse(Slave.restart_interval, cv2.error)
        def _handle_image_thread():
            camera = cv2.VideoCapture(0)
            camera.set(3, Slave.width)
            camera.set(4, Slave.height)
            while True:
                time.sleep(Slave.interval)
                ret, image = camera.read()
                ret, image = cv2.imencode('.jpg', image, Slave.quality)
                msg = Message('image', Slave.detail, image.tobytes())
                self.send_queue.put(msg)

        handle_image_thread = Thread(target=_handle_image_thread)
        handle_image_thread.setDaemon(True)
        return handle_image_thread

    def handle_serial_thread(self):
        def _handle_serial_thread():
            while True:
                msg = self.serial_queue.get()
                print(msg)

        handle_serial_thread = Thread(target=_handle_serial_thread)
        handle_serial_thread.setDaemon(True)
        return handle_serial_thread

    def handle_audio_thread(self):
        @undead_curse(Slave.restart_interval, sd.PortAudioError)
        def _handle_audio_thread():
            msg = self.audio_queue.get()
            sampling_rate, block_size, channel_num = msg.unpack_detail()
            with sd.OutputStream(sampling_rate, block_size, channels=channel_num) as output_stream:
                while True:
                    msg = self.audio_queue.get()
                    audio = np.fromstring(msg.value, np.float32)
                    output_stream.write(audio)

        handle_audio_thread = Thread(target=_handle_audio_thread)
        handle_audio_thread.setDaemon(True)
        return handle_audio_thread

    def mainloop(self, new_loop=False):
        self.handle_image_thread().start()
        self.handle_serial_thread().start()
        self.handle_audio_thread().start()
        super().mainloop(new_loop)


if __name__ == '__main__':
    test_slave = Slave('localhost', 8080, '123456')
    test_slave.mainloop()
