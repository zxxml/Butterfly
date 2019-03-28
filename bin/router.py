#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ssl

import click

from bin import utils
from butterfly.router import Router


@click.command()
@click.argument('host')
@click.argument('port', type=click.IntRange(1, 65535))
@click.argument('passwd')
@click.option('--crt', type=click.Path(True))
@click.option('--key', type=click.Path(True))
def main(host, port, passwd, crt, key):
    ssl_ctx = None
    if not utils.is_any_none(key, crt):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(crt, key)
    router = Router(host, port, passwd, ssl_ctx)
    router.mainloop()


if __name__ == '__main__':
    utils.fix_signal()
    main()
