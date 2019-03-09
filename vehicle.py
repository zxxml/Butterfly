#!/usr/bin/python3
# -*- coding: utf-8 -*-
import signal
import ssl

import click


@click.group(context_settings={'help_option_names': ('-h', '--help')})
def main():
    pass


@click.command()
@click.option('--host', default='localhost', show_default=True, help='监听地址')
@click.option('--port', type=click.IntRange(1, 65535), default=8080, show_default=True, help='监听端口')
@click.option('--passwd', default='123456', show_default=True, help='服务器密码')
@click.option('--crt', help='公钥文件路径，留空以关闭SSL/TLS')
@click.option('--key', help='私钥文件路径，留空以关闭SSL/TLS')
def server(host, port, passwd, crt, key):
    from server import Server
    ssl_context = None
    if crt is not None and key is not None:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(crt, key)
    secure_server = Server(host, port, passwd, ssl_context)
    secure_server.mainloop()


def client(host, port, passwd, protocol, module, _class):
    import importlib
    ssl_context = None
    if protocol == 'wss':
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.set_default_verify_paths()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
    module = importlib.import_module(module)
    _class = getattr(module, _class)
    secure_client = _class(host, port, passwd, ssl_context)
    secure_client.mainloop()


@click.command()
@click.option('--host', default='localhost', show_default=True, help='服务器地址')
@click.option('--port', type=click.IntRange(1, 65535), default=8080, show_default=True, help='服务器端口')
@click.option('--passwd', default='123456', show_default=True, help='服务器密码')
@click.option('--protocol', type=click.Choice(('ws', 'wss')), default='ws', show_default=True, help='WebSocket协议')
def slave(host, port, passwd, protocol):
    client(host, port, passwd, protocol, 'slave', 'Slave')


@click.command()
@click.option('--host', default='localhost', show_default=True, help='服务器地址')
@click.option('--port', type=click.IntRange(1, 65535), default=8080, show_default=True, help='服务器端口')
@click.option('--passwd', default='123456', show_default=True, help='服务器密码')
@click.option('--protocol', type=click.Choice(('ws', 'wss')), default='ws', show_default=True, help='WebSocket协议')
def master(host, port, passwd, protocol):
    client(host, port, passwd, protocol, 'master', 'Master')


if __name__ == '__main__':
    # 将键盘中断信号的handler恢复为SIG_DFL，修复asyncio在Windows上的bug
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main.add_command(server)
    main.add_command(slave)
    main.add_command(master)
    main()
