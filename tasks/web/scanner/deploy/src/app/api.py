import json

import redis.asyncio as redis
import fastapi
from fastapi import APIRouter, HTTPException, Depends

from app import miner, config

api = APIRouter(
    prefix="/api",
)

redis_pool = redis.ConnectionPool.from_url(config.get_config().redis_url)


async def get_redis():
    red = redis.Redis.from_url(config.get_config().redis_url)
    try:
        yield red
    finally:
        await red.aclose()


@api.get("/")
def index():
    return {"hello": "world"}


@api.post('/mine')
async def mine(req: fastapi.Request, red: redis.Redis = Depends(get_redis)):
    try:
        body = await req.json()
    except Exception:
        raise HTTPException(status_code=422, detail="JSON body expected")

    url = body.get('url')
    headers = body.get('headers')
    version = body.get('version')

    if url is None:
        raise HTTPException(status_code=422, detail="URL should be present")

    task = miner.mine_task.delay(url, headers, version)

    mine_info = {
        'request': {
            'url': url,
            'headers': headers,
            'version': version
        },
        'task_id': str(task),
    }
    await red.lpush('mines', json.dumps(mine_info))

    return {'task_id': str(task)}


@api.get('/mine/{task_id}')
def get_mine_result(task_id):
    res = miner.mine_task.app.AsyncResult(task_id)
    if not res.ready():
        return {'task_id': task_id, 'ready': False}

    try:
        result = res.get()
    except Exception as e:
        return {'task_id': task_id, 'ready': True, 'success': False, 'result': str(e)}
    return {'task_id': task_id, 'ready': True, 'result': result, 'success': True}


@api.get('/mine')
async def get_all_mines(red: redis.Redis = Depends(get_redis)):
    data = await red.lrange('mines', 0, -1)
    out = []
    for v in data:
        v = json.loads(v)
        out.append(v)
    return {'mines': out}
