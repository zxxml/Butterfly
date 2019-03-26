#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ujson

import requests
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

from butterfly import tricks
from butterfly.utils import BlackBox


class Sight(BlackBox):
    # Sight is powered by Face++, an AI company
    # which provided cheap or even free service
    url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

    def __init__(self, api_key: str, api_sec: str, **kwargs):
        # set buffer size to 2 so as to make sure that
        # every img sent successfully will be processed
        # however, sometimes you may failed sending it
        # use `recv_q.put_anyway()` to ignore this error
        super().__init__(max_size=2, **kwargs)
        self.payload = {'api_key': api_key, 'api_secret': api_sec}

    @tricks.undead_curse(2, print, HTTPError, RequestException)
    def run(self):
        self.mainloop()

    @tricks.new_game_plus
    def mainloop(self):
        # get an img from `recv_q`
        # and encode it in base64
        width, height, img = self.recv_q.get()
        data = base64.b64encode(img)
        # prepare request data
        # and ask for detection
        payload = self.payload.copy()
        payload['image_base64'] = data
        resp = requests.post(self.url, data=payload, timeout=2)
        result = ujson.loads(resp.content)
        # do nothing if failed to detect
        # may check `error_message` instead
        if 'faces' not in result:
            return None
        # extract faces from result
        # and convert dict to tuple
        # a rect contains x, y, width and height
        rects = map(lambda x: x['face_rectangle'], result['faces'])
        rects = map(lambda x: (x['left'], x['top'], x['width'], x['height']), rects)
        self.send_q.put((width, height, tuple(rects)))
