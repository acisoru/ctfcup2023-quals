import requests

import base64
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def restore_message(json_data):
    json_data = base64.b64decode(json_data)
    json_data = json.loads(json_data)
    print(json_data)
    private_key_data = json_data["key"]
    encrypted_message = json_data["task"]["c"]

    private_key_data = private_key_data.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_data, password=None, backend=default_backend())

    # Декодируем и расшифровываем сообщение
    encrypted_message = base64.b64decode(encrypted_message)

    # Длина ключа в битах
    key_length = private_key.key_size

    # Разбиваем зашифрованное сообщение на блоки
    num_blocks = len(encrypted_message) // (key_length // 8)

    decrypted_message = b''

    # Расшифровываем каждый блок
    for i in range(num_blocks):
        start = i * (key_length // 8)
        end = (i + 1) * (key_length // 8)
        block = encrypted_message[start:end]
        decrypted_block = private_key.decrypt(block, padding.PKCS1v15())
        decrypted_message += decrypted_block
        print(decrypted_message)
    return decrypted_message.decode('utf-8')

def main():
    from sys import argv
    if(len(argv) < 2):
        print("Usage: python3 solve.py https://example.com")
        return
    url = argv[1]
    session = requests.Session()
    last = session.get(f'{url}/generate-task')
    for i in range(1337):
        ans = restore_message(session.cookies.get("session"))
        print(ans)
        r = session.post(f'{url}/check-task',json={"input": 1},cookies=last.cookies,proxies={'http':"http://localhost:8080"})
        s = r.json()
        if(s['flag']):
            print(s['flag'])
            return

if __name__ == "__main__":
    main()