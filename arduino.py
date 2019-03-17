#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from serial import Serial as _Serial
from serial import SerialException

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

    @undead_curse(5, print, FileNotFoundError, SerialException)
    def mainloop(self):
        with _Serial(port=self.port, baudrate=self.band_rate) as serial:
            while True:
                packet = self.recv_queue.get()
                serial.write(repr(packet))
