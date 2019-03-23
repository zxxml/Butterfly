#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from serial import Serial as serial_Serial, SerialException
from serial.tools.list_ports import comports

from core.ground import BlackBox
from core.magic import undead_curse


@dataclass
class SerialConfig:
    port: str
    baud_rate: int


class Serial(BlackBox):
    """串口黑盒从recv_queue中获取数据，然后将它原样写入到串口中。
    串口黑盒拥有自动检测端口的能力，在指定的端口不存在的情况下，它将使用检测到的第一个端口。
    """

    def __init__(self, config: SerialConfig, **kwargs):
        super().__init__(**kwargs)
        self.port = config.port
        self.band_rate = config.baud_rate

    def detect_port(self):
        ports = [each.device for each in comports()]
        return ports[0] if ports and self.port not in ports else self.port

    def detect_baud_rate(self):
        return self.band_rate

    @undead_curse(5, print, FileNotFoundError, SerialException)
    def mainloop(self):
        port, baud_rate = self.detect_port(), self.detect_baud_rate()
        with serial_Serial(port=port, baudrate=baud_rate) as serial:
            while True:
                item = self.recv_queue.get()
                serial.write(item)
