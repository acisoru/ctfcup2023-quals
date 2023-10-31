import base64
import json
import secrets
import socket
import sys
from hashlib import md5

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from geometry import SymmetryGroup

from flag import flag

def recvline(s: socket.socket):
    b = b''

    while not b or not b.endswith(b'\n'):
        print(b)
        b += s.recv(1)

    return b

def main():
    io = socket.socket()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    io.connect((HOST, PORT))

    diffie_hellman_base = SymmetryGroup(1337, json.loads(recvline(io)))

    client_private = secrets.randbelow(2 ** 1337)
    client_public = diffie_hellman_base ** client_private

    io.sendall(json.dumps(client_public.vertex_order).encode() + b'\n')

    server_public = SymmetryGroup(1337, json.loads(recvline(io)))

    shared_secret = server_public ** client_private

    secret_key = md5(str(shared_secret).encode()).digest()

    cipher = AES.new(secret_key, AES.MODE_ECB)

    io.sendall(base64.b64encode(cipher.encrypt(pad(flag.encode(), 16))) + b'\n')

if __name__ == "__main__":
    main()
