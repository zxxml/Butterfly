#!/usr/bin/python3
# -*- coding: utf-8 -*-


class Server:
    chart = {'master': 'slave', 'slave': 'master'}
    url_template = '{0}://{1}:{2}/?passwd={3}&client_type={4}'


class Client:
    url_template = Server.url_template
    restart_interval = 5


class Slave(Client):
    # @formatter:off
    width, height = 640, 480    # 摄像头分辨率
    quality = (1, 60)           # 图像压缩质量（cv2.IMWRITE_JPEG_QUALITY = 1）
    interval = 1 / 30           # 最高摄像头回传报文传输速率
    # @formatter:on
    detail = '{0}x{1}'.format(width, height)


class Master(Client):
    # @formatter:off
    sampling_rate = 44100               # 麦克风采样率
    block_size = sampling_rate // 20    # 帧大小
    channel_num = 2                     # 麦克风声道数
    # @formatter:on
    detail = '{0}x{1}x{2}'.format(sampling_rate, block_size, channel_num)


class MasterApp:
    # @formatter:off
    width, height = 640, 480    # 默认窗口大小
    interval = Slave.interval   # 最高摄像头回传报文显示速率
    value_threshold = 5120      # 手柄摇杆灵敏度
    # @formatter:on
    action_table = {0: 'vehicle', 1: 'vehicle', 3: 'camera', 4: 'camera'}
    detail_table = {0: 'vertical', 1: 'horizontal', 3: 'vertical', 4: 'horizontal'}


class MasterButton:
    action_table = {'left_stick': 'vehicle', 'right_stick': 'camera'}
    detail_table = {'up_btn': 'vertical', 'down_btn': 'vertical', 'left_btn': 'horizontal', 'right_btn': 'horizontal'}
    value_table = {'up_btn': -32767, 'down_btn': 32767, 'left_btn': -32767, 'right_btn': 32767}
    button_table = {'a_btn': 0, 'b_btn': 1, 'x_btn': 2, 'y_btn': 3}
