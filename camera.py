#!/usr/bin/python3
# -*- coding: utf-8 -*-
from cv2 import VideoCapture, flip, imencode
from cv2 import error as cv2_error
from dataclasses import dataclass

from ground import BlackBox
from magic import undead_curse


@dataclass
class CameraConfig:
    width: int
    height: int
    quality: int
    vertical_flip: bool
    horizontal_flip: bool


class Camera(BlackBox):
    def __init__(self, config: CameraConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.camera: VideoCapture = None

    def read(self):
        _, image = self.camera.read()
        height, width = image.shape[0:2]
        _, image = imencode('.jpg', image, (1, self.config.quality))
        image = flip(image, 0) if self.config.vertical_flip else image
        image = flip(image, 1) if self.config.horizontal_flip else image
        return width, height, image

    @undead_curse(5, print, cv2_error)
    def mainloop(self):
        self.camera = VideoCapture(0)
        self.camera.set(3, self.config.width)
        self.camera.set(4, self.config.height)
        while True:
            item = self.read()
            self.send_queue.put(item)
