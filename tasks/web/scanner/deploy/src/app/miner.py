import asyncio
import yarl
import shlex
import subprocess
import aiohttp
import aiohttp.client_exceptions
from celery import shared_task


class InvalidHostException(Exception):
    def __init__(self, hostname):
        self.hostname = hostname
        self.msg = self.get_verbose_message(hostname)

    def __str__(self):
        return self.msg

    def get_verbose_message(self, hostname):
        ip = self._resolve(hostname)
        return "Failed to connect to host = {} (ip = {})".format(hostname, ip)

    def _resolve(self, host):
        return subprocess.check_output(f"dig {host} +short", stderr=subprocess.STDOUT, shell=True)


async def mine(url, headers=None, version=None, timeout=5):
    if not headers:
        headers = dict()
    if not version:
        version = '1.1'

    req_headers = {}
    for k, v in headers.items():
        req_headers[str(k).lower()] = v
    req_headers['connection'] = 'Close'

    try:
        async with aiohttp.ClientSession(headers=req_headers, version=version) as session:
            async with session.request('GET', url, timeout=timeout) as resp:
                cntn = await resp.content.read()
                hdrs = dict()
                for h in resp.headers.keys():
                    hdrs[h] = resp.headers.getone(h)
                return {'content': cntn, 'headers': hdrs}
    except aiohttp.client_exceptions.InvalidURL as e:
        raise e
    except aiohttp.client_exceptions.ClientConnectionError:
        raise InvalidHostException(shlex.quote(yarl.URL(url).host))


@shared_task
def mine_task(url, headers=None, version=None):
    res = asyncio.run(mine(url, headers, version))
    return res
