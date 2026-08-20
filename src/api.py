from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
from .tasks import run_account_session

app = FastAPI()

class RunRequest(BaseModel):
    account_id: int
    profile_spec: dict
    proxy_url: str
    twofa_secret: str | None = None
    account_login: str | None = None
    account_password: str | None = None

@app.post('/run')
def enqueue_run(req: RunRequest):
    # enqueue Celery task
    task = run_account_session.delay(req.account_id, req.profile_spec, req.proxy_url, req.twofa_secret, req.account_login, req.account_password)
    return {"task_id": task.id}

@app.get('/health')
def health():
    return {"status": "ok"}
