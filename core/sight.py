#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ujson import loads as ujson_loads

from dataclasses import asdict, dataclass
from requests import post as requests_post

from core.ground import BlackBox


@dataclass
class SightConfig:
    api_key: str
    api_secret: str
    return_landmark: int = None
    return_attributes: str = None
    calculate_all: int = None
    face_rectangle: str = None
    beauty_score_min: int = None
    beauty_score_max: int = None

    def unpack(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


class Sight(BlackBox):
    def __init__(self, config: SightConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def detect_faces(self, image):
        api_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
        payload = self.config.unpack()
        files = {'image_file': image.tobytes()}
        r = requests_post(api_url, data=payload, files=files, timeout=2)
        content = ujson_loads(r.content)
        if 'error_message' in content:
            return content['error_message']
        faces = content['faces']

    def mainloop(self, **kwargs):
        image = self.recv_queue.get()
        faces = self.detect_faces(image)
        return faces


if __name__ == '__main__':
    import cv2

    api_key = 'bA20twdRcbtD0yjyUPhZzeopq4jmIOAH'
    api_secret = '83kb7C4P7MAUBpH8SkX-idR5q2z_fiby'
    test_sight_config = SightConfig(api_key, api_secret)
    test_sight = Sight(test_sight_config)
    img = cv2.imread('test.jpg')
    _, img = cv2.imencode('.jpg', img, (1, 20))
    resp = test_sight.detect_faces(img)
    print(resp.json())
