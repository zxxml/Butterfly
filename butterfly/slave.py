#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ssl

from dataclasses import dataclass

from butterfly import tricks
from butterfly.body import Body
from butterfly.eye import Eye
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
    ssl_ctx: ssl.SSLContext = None

    def __post_init__(self):
        self.eye_node = Node(self.host, self.port, self.passwd, 'slave_eye', 'master_eye', self.ssl_ctx)
        self.body_node = Node(self.host, self.port, self.passwd, 'slave_body', 'master_body', self.ssl_ctx)
        self.eye = Eye(self.width, self.height, self.v_flip, self.h_flip, self.quality)
        self.body = Body(self.com_port, self.baud_rate)

    def mainloop(self):
        pass

    @tricks.new_game_plus
    def handle_cam(self):
        pass

    @tricks.new_game_plus
    def handle_ser(self):
        pass
