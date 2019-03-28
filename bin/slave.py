#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ssl

import click

from bin import utils
from butterfly.slave import Slave


@click.command()
@click.argument('host')
@click.argument('port', type=click.IntRange(1, 65535))
@click.argument('passwd')
@click.option('--width', type=click.INT, default=640)
@click.option('--height', type=click.INT, default=480)
@click.option('--v_flip', is_flag=True)
@click.option('--h_flip', is_flag=True)
@click.option('--quality', type=click.IntRange(0, 100), default=60)
@click.option('--com_port')
@click.option('--baud_rate', type=click.INT, default=9600)
@click.option('--spl_rate', type=click.INT, default=44100)
@click.option('--ch_num', type=click.INT, default=2)
@click.option('--enable_ssl', is_flag=True)
def main(enable_ssl, **kwargs):
    ssl_ctx = None
    if enable_ssl:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.set_default_verify_paths()
    slave = Slave(ssl_ctx=ssl_ctx, **kwargs)
    slave.mainloop()


if __name__ == '__main__':
    utils.fix_signal()
    main()
