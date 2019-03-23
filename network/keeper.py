#!/usr/bin/python3
# -*- coding: utf-8 -*-
import base64
import zlib

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.illusions import vow_of_silence


class Keeper:
    @staticmethod
    def generate_key(passwd: bytes):
        kdf = PBKDF2HMAC(SHA256(), 32, passwd, 100000, default_backend())
        return base64.urlsafe_b64encode(kdf.derive(passwd))

    def __init__(self, passwd: bytes):
        self.key = self.generate_key(passwd)
        self.fernet = Fernet(self.key)

    @vow_of_silence(zlib.error)
    def encrypt(self, data: bytes):
        data = self.fernet.encrypt(data)
        return zlib.compress(data)

    @vow_of_silence(zlib.error)
    def decrypt(self, data: bytes):
        data = zlib.decompress(data)
        return self.fernet.decrypt(data)
