import os.path

import uvicorn
from app.app import create_app

app = create_app(static_root=os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"))
celery = app.celery_app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
