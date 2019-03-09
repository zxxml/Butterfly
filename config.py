#!/usr/bin/python3
# -*- coding: utf-8 -*-


class Server:
    chart = {'master': 'slave', 'slave': 'master'}
    url_template = '{0}://{1}:{2}/?passwd={3}&client_type={4}'
    interval = 1 / 60


class Client:
    url_template = Server.url_template
    interval = Server.interval
    restart_interval = 5


class Slave(Client):
    width, height = 640, 480
    quality = (1, 60)  # cv2.IMWRITE_JPEG_QUALITY = 1
    detail = '{0}x{1}'.format(width, height)


class Master(Client):
    sampling_rate = 48000
    block_size = sampling_rate // 10
    channel_num = 2
    detail = '{0}x{1}x{2}'.format(sampling_rate, block_size, channel_num)


class MasterWindow:
    width, height = 640, 480
    interval = Master.interval


class MasterButton:
    action_table = {'left_stick': 'vehicle', 'right_stick': 'camera'}
    detail_table = {'up_btn': 'up', 'down_btn': 'down', 'left_btn': 'left', 'right_btn': 'right'}
