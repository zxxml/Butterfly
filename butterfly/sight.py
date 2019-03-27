#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import time
import ujson

import cv2
import requests
from requests import RequestException
from skimage.measure import compare_mse
from urllib3.exceptions import HTTPError

from butterfly import tricks
from butterfly.utils import BlackBox


class Sight(BlackBox):
    # Sight is powered by Face++, an AI company
    # which provided cheap or even free service
    url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

    def __init__(self, api_key: str, api_sec: str, **kwargs):
        # set limited buffer size so as to make sure that
        # every img sent successfully will be processed
        # however, sometimes you may failed to send
        # use `recv_q.put_anyway()` to ignore this error
        super().__init__(max_size=10, **kwargs)
        self.threads = [Detr(api_key, api_sec) for _ in range(10)]

    def run(self):
        for each in self.threads:
            each.send_q = self.send_q
            each.setDaemon(True)
            each.start()
        self.mainloop()

    @tricks.new_game_plus
    def mainloop(self):
        for each in self.threads:
            item = self.recv_q.get()
            each.recv_q.put_anyway(item)
            time.sleep(1 / 10)


class Detr(BlackBox):
    # Detr is powered by Face++, an AI company
    # which provided cheap or even free service
    url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

    def __init__(self, api_key: str, api_sec: str, **kwargs):
        super().__init__(max_size=1, **kwargs)
        self.old_img = None
        self.payload = {'api_key': api_key, 'api_secret': api_sec}

    @tricks.new_game_plus
    def run(self):
        width, height, img_jpg = self.recv_q.get()
        img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)
        if self.worth_updating(img):
            rects = self.detect(img_jpg)
            if rects is None:
                return None
            self.send_q.put((width, height, rects))

    def worth_updating(self, img):
        # use gray scale img and small size
        # in order to reduce the computation
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        temp = cv2.resize(gray, (256, 256))
        print('recv')
        if self.old_img is None:
            self.old_img = temp
            return True
        score = compare_mse(temp, self.old_img)
        print(score, 'aaa')
        if score >= 0.9:
            self.old_img = temp
            return True
        return False

    @tricks.vow_of_silence(HTTPError, RequestException)
    def detect(self, img_jpg):
        data = base64.b64encode(img_jpg)
        # prepare request data
        # and ask for detection
        payload = self.payload.copy()
        payload['image_base64'] = data
        resp = requests.post(self.url, data=payload, timeout=2)
        result = ujson.loads(resp.content)
        # do nothing if failed to detect
        # may check `faces` instead
        if 'error_message' in result:
            print(result['error_message'])
            return None
        # extract faces from result
        # and convert dict to tuple
        # a rect contains x, y, width and height
        rects = map(lambda x: x['face_rectangle'], result['faces'])
        rects = map(lambda x: (x['left'], x['top'], x['width'], x['height']), rects)
        return tuple(rects)
