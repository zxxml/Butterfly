#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cv2

from butterfly import tricks
from butterfly.utils import BlackBox


class Eye(BlackBox):
    def __init__(self, width: int, height: int, v_flip: bool,
                 h_flip: bool, quality: int, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.v_flip = v_flip
        self.h_flip = h_flip
        self.quality = (cv2.IMWRITE_JPEG_QUALITY, quality)
        self.eye: cv2.VideoCapture = None

    @tricks.undead_curse(2, print, cv2.error)
    def run(self):
        self.eye = cv2.VideoCapture(0)
        self.eye.set(3, self.width)
        self.eye.set(4, self.height)
        self.mainloop()

    @tricks.new_game_plus
    def mainloop(self):
        # item contains width, height and img
        # img is JPEG encoded or None if failed
        item = self.read()
        self.send_q.put(item)

    def read(self):
        ret, img = self.eye.read()
        if self.v_flip:
            img = cv2.flip(img, 0)
        if self.h_flip:
            img = cv2.flip(img, 1)
        height, width = img.shape[0:2]
        ret, img = cv2.imencode('.jpg', img, self.quality)
        return width, height, img
