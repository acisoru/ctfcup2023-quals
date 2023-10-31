import os.path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from app.worker import create_celery
from app.api import api


def create_exception_handler(static_root=''):
    async def redirect_all_requests_to_frontend(request: Request, exc: HTTPException):
        with open(os.path.join(static_root, 'index.html')) as f:
            return HTMLResponse(f.read())

    return redirect_all_requests_to_frontend


def create_app(static_root=None):
    app = FastAPI()
    app.include_router(api)
    app.mount("/assets", StaticFiles(directory=static_root + '/assets'), name="assets")
    app.add_exception_handler(404, create_exception_handler(static_root))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.celery_app = create_celery()
    return app
