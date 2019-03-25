#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64

import numpy as np
import sounddevice as sd

from butterfly import tricks
from butterfly.utils import BlackBox


class Mouth(BlackBox):
    def __init__(self, spl_rate: int, ch_num: int, **kwargs):
        super().__init__(**kwargs)
        self.spl_rate = spl_rate
        self.ch_num = ch_num

    @tricks.undead_curse(2, print, sd.PortAudioError)
    def run(self):
        with sd.OutputStream(self.spl_rate, self.spl_rate // 10,
                             channels=self.ch_num) as stream:
            self.mainloop(stream)

    @tricks.new_game_plus
    def mainloop(self, stream):
        data = self.recv_q.get()
        temp = base64.b64decode(data)
        audio = np.fromstring(temp, np.float32)
        stream.write(audio)
