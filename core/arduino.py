#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from serial import Serial as _Serial
from serial import SerialException
from serial.tools.list_ports import comports

from ground import BlackBox
from magic import undead_curse


@dataclass
class SerialConfig:
    port: str
    baud_rate: int


class Serial(BlackBox):
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
        with _Serial(port=port, baudrate=baud_rate) as serial:
            while True:
                item = self.recv_queue.get()
                serial.write(item)
