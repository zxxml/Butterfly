#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ssl

import click

from bin import utils
from butterfly.master import Master


@click.command()
@click.argument('host')
@click.argument('port', type=click.IntRange(1, 65535))
@click.argument('passwd')
@click.option('--api_key', required=True)
@click.option('--api_sec', required=True)
@click.option('--spl_rate', type=click.INT, default=44100)
@click.option('--ch_num', type=click.INT, default=2)
@click.option('--enable_ssl', is_flag=True)
def main(enable_ssl, **kwargs):
    ssl_ctx = None
    if enable_ssl:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.set_default_verify_paths()
    slave = Master(ssl_ctx=ssl_ctx, **kwargs)
    slave.mainloop()


if __name__ == '__main__':
    utils.fix_signal()
    main()
