import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import TwoFASession

BASE_URL = "https://your-domain.example"  # override via env in production

def create_twofa_session(account_id: int, expires_seconds: int = 300) -> dict:
    token = secrets.token_urlsafe(16)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_seconds)
    db: Session = SessionLocal()
    try:
        tf = TwoFASession(token=token, account_id=account_id, expires_at=expires_at)
        db.add(tf)
        db.commit()
        db.refresh(tf)
        return {"token": token, "url": f"{BASE_URL}/2fa/{token}", "expires_at": expires_at}
    finally:
        db.close()

def submit_twofa_code(token: str, code: str) -> dict:
    db: Session = SessionLocal()
    try:
        tf = db.query(TwoFASession).filter(TwoFASession.token == token).first()
        if not tf:
            raise HTTPException(status_code=404, detail="token not found")
        if tf.status != 'pending':
            raise HTTPException(status_code=400, detail="session not pending")
        tf.code = code
        tf.status = 'submitted'
        tf.used_at = datetime.utcnow()
        db.add(tf)
        db.commit()
        return {"ok": True}
    finally:
        db.close()

def get_twofa_status(token: str) -> Optional[dict]:
    db: Session = SessionLocal()
    try:
        tf = db.query(TwoFASession).filter(TwoFASession.token == token).first()
        if not tf:
            return None
        return {"token": tf.token, "status": tf.status, "code": tf.code}
    finally:
        db.close()
