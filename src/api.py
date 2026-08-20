from fastapi import FastAPI, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import os
from .tasks import run_account_session
from .twofa import create_twofa_session, submit_twofa_code, get_twofa_status

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
    task = run_account_session.delay(req.account_id, req.profile_spec, req.proxy_url, req.twofa_secret, req.account_login, req.account_password)
    return {"task_id": task.id}

@app.get('/health')
def health():
    return {"status": "ok"}

# 2FA web endpoints
@app.get('/2fa/{token}', response_class=HTMLResponse)
def twofa_form(token: str):
    # simple HTML form for manual code entry
    html = f"""
    <html>
      <head><title>Enter 2FA code</title></head>
      <body>
        <h3>Enter 2FA code for token {token}</h3>
        <form method="post" action="/2fa/{token}/submit">
          <input type="text" name="code" placeholder="123456" />
          <button type="submit">Submit</button>
        </form>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post('/2fa/{token}/submit')
def twofa_submit(token: str, code: str = Form(...)):
    submit_twofa_code(token, code)
    return RedirectResponse(url=f"/2fa/{token}", status_code=303)

@app.get('/2fa/{token}/status')
def twofa_status(token: str):
    s = get_twofa_status(token)
    if not s:
        return {"status": "not_found"}
    return s
