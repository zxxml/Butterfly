#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @formatter:off
"""全局配置及类属性集散地。"""


class Server:
    chart = {'master': 'slave', 'slave': 'master'}
    url_template = '{0}://{1}:{2}/?passwd={3}&client_type={4}'


class Client:
    restart_interval = 5  # 自动重启间隔
    url_template = Server.url_template


class Slave(Client):
    image_width, image_height = 1280, 720   # 摄像头分辨率，可以高于摄像头支持的最高分辨率
    image_quality = (1, 60)                 # 图像压缩质量（cv2.IMWRITE_JPEG_QUALITY = 1）
    image_interval = 1 / 30                 # 摄像头帧率，不建议高于摄像头支持的最高帧率


class Master(Client):
    sampling_rate = 44100   # 麦克风采样率
    block_size = 1024       # 帧大小
    channel_num = 2         # 麦克风声道数


class MasterApp:
    width, height = 1280, 720               # 默认窗口大小
    image_interval = Slave.image_interval   # 显示帧率，建议和摄像头帧率保持一致
    action_table = {0: 'vehicle', 1: 'vehicle', 3: 'camera', 4: 'camera'}
    detail_table = {0: 'vertical', 1: 'horizontal', 3: 'vertical', 4: 'horizontal'}


class MasterButton:
    action_table = {'left_stick': 'vehicle', 'right_stick': 'camera'}
    detail_table = {'up_btn': 'vertical', 'down_btn': 'vertical', 'left_btn': 'horizontal', 'right_btn': 'horizontal'}
    value_table = {'up_btn': -32767, 'down_btn': 32767, 'left_btn': -32767, 'right_btn': 32767}
    button_table = {'a_btn': 0, 'b_btn': 1, 'x_btn': 2, 'y_btn': 3}
