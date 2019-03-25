#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import ujson

import requests

from butterfly import tricks
from butterfly.utils import BlackBox


class Sight(BlackBox):
    # Sight is powered by Face++, an AI company
    # which provided cheap or even free service
    url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

    def __init__(self, api_key: str, api_sec: str, **kwargs):
        super().__init__(max_size=2, **kwargs)
        self.payload = {'api_key': api_key, 'api_secret': api_sec}

    def run(self):
        self.mainloop()

    @tricks.new_game_plus
    def mainloop(self):
        # get an img from recv_q
        # and encode it in base64
        img = self.recv_q.get()
        data = base64.b64encode(img)
        # prepare request data
        # and ask for detection
        payload = self.payload.copy()
        payload['image_base64'] = data
        resp = requests.post(self.url, data=payload)
        result = ujson.loads(resp.content)
        # do nothing if failed to detect
        # may check error_message instead
        if 'faces' not in result:
            return None
        # extract faces from result
        # and convert dict to tuple
        # a rect contains x, y, width and height
        rects = map(lambda x: x['face_rectangle'], result['faces'])
        rects = map(lambda x: (x['left'], x['top'], x['width'], x['height']), rects)
        self.send_q.put(tuple(rects))
