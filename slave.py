#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread

from core.arduino import Serial, SerialConfig
from core.camera import Camera, CameraConfig
from core.client import Client
from core.magic import new_game_plus
from core.server import ServerConfig
from packet import Packet


class Slave:
    def __init__(self, server_config: ServerConfig,
                 camera_config: CameraConfig, serial_config: SerialConfig):
        normal_config = server_config.to_client_config('slave', 'normal')
        video_config = server_config.to_client_config('slave', 'video')
        self.normal_client = Client(normal_config, daemon=True)
        self.video_client = Client(video_config, daemon=True)
        self.camera = Camera(camera_config, daemon=True)
        self.serial = Serial(serial_config, daemon=True)

    @new_game_plus
    def handle_normal(self):
        packet = self.normal_client.recv_queue.get()
        packet = Packet.unpack(packet)
        self.serial.recv_queue.put(repr(packet))

    @new_game_plus
    def handle_video(self):
        width, height, image = self.camera.send_queue.get()
        detail = '{0}x{1}'.format(width, height)
        packet = Packet('video', detail, image.tobytes())
        self.video_client.send_queue.put(packet.pack())

    def mainloop(self):
        self.normal_client.start()
        self.video_client.start()
        self.camera.start()
        self.serial.start()
        Thread(target=self.handle_normal).start()
        Thread(target=self.handle_video).start()


if __name__ == '__main__':
    test_server_config = ServerConfig('localhost', 8080, '123456')
    test_camera_config = CameraConfig(640, 480, 60, True, True)
    test_serial_config = SerialConfig('COM4', 9600)
    test_slave = Slave(test_server_config, test_camera_config, test_serial_config)
    test_slave.mainloop()
