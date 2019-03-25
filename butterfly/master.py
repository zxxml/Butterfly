#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ssl

from dataclasses import dataclass
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.widget import Widget

from butterfly.node import Node


@dataclass
class Master:
    host: str
    port: int
    passwd: str
    ssl_ctx: ssl.SSLContext = None

    def __post_init__(self):
        self.eye_node = Node(self.host, self.port, self.passwd, 'master_eye', 'slave_eye', self.ssl_ctx)
        self.body_node = Node(self.host, self.port, self.passwd, 'master_body', 'slave_body', self.ssl_ctx)

    def mainloop(self):
        self.eye_node.start()
        self.body_node.start()


class MasterWin(Widget):
    Builder.load_file('master.kv')
    Window.size = (640, 480)
