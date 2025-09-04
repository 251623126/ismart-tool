#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import random

class UP366Encrypt:
    ENCRYPT_TYPES = {
        11: "submitLogToken",
        22: "loginEncryptionParameter",
        33: "sendSMSToken",
        44: "commonEncryptToken",
        55: "DAY_EN_SUBMIT",
        66: "DAY_WRITE_SUBMIT",
        77: "PIGAI_ASSESS_MARK",
        88: "FRONT_CORRECT_ASYNC",
        90: "FRONT_OCR_ASYNC",
        91: "_!@#usertoken!@#_",
        99: "-android-7654321"
    }

    @staticmethod
    def encrypt(param: str, etype: int, rand: int | None = None) -> str:
        key = UP366Encrypt.ENCRYPT_TYPES.get(etype)
        if not key:
            raise ValueError(f"未知加密类型: {etype}")
        if rand is None:
            rand = random.getrandbits(64)
        a = hashlib.md5(str(rand).encode()).hexdigest()
        b = hashlib.md5((param + key + a).encode()).hexdigest()
        return a[:10] + b + a[-22:]

if __name__ == "__main__":
    test_input = "17856000000e8118e9fd56b6cca9e02f470bd8ca968"
    print("加密结果:", UP366Encrypt.encrypt(test_input, 22))
