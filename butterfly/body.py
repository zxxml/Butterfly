#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
from serial.tools.list_ports import comports

from butterfly import tricks
from butterfly.utils import BlackBox


class Body(BlackBox):
    def __init__(self, port: str, baud_rate: int, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.baud_rate = baud_rate

    @tricks.undead_curse(2, print, FileNotFoundError, serial.SerialException)
    def run(self):
        port = self.detect_port()
        with serial.Serial(port, self.baud_rate) as ser:
            self.mainloop(ser)

    @tricks.new_game_plus
    def mainloop(self, ser):
        item = self.recv_q.get()
        ser.write(item)

    def detect_port(self):
        ports = [each.device for each in comports()]
        if ports and self.port not in ports:
            return ports[0]
        return self.port
