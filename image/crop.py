#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image


def crop_bounding_box(image):
    image = np.asarray(image)
    indices = np.argwhere(image[:, :, 3] != 0)
    x, y = np.min(indices, axis=0)
    width, height = np.max(indices, axis=0)
    width, height = width - x, height - y
    return x, y, width, height


def main(image_path, output_path=None):
    """裁剪图片的最小包围盒。"""
    image = Image.open(image_path)
    image = image.convert('RGBA')
    x, y, width, height = crop_bounding_box(image)
    image = image.crop((y, x, y + height, x + width))
    image.save(image_path if output_path is None else output_path)


def mainloop():
    while True:
        image_path = input()
        main(image_path)


if __name__ == '__main__':
    mainloop()
