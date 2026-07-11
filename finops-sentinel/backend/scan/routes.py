import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from auth.database import SessionLocal
from auth.models import User
from scan.orchestrator import run_scan

router = APIRouter()

from auth.security import SECRET_KEY, ALGORITHM


def _get_user_from_token(token: str) -> User | None:
    """Manually validate JWT and fetch user from DB (used for WebSocket auth)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        db: Session = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    except JWTError:
        return None


import logging

logger = logging.getLogger(__name__)

@router.websocket("/api/scan/ws")
async def scan_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        # Step 1: Wait for the client to send mode + token
        raw = await websocket.receive_text()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send_json({"step": "auth", "status": "error", "message": "Invalid JSON in initial message."})
            await websocket.close()
            return

        token = data.get("token")
        mode = data.get("mode", "mock")

        if not token:
            await websocket.send_json({"step": "auth", "status": "error", "message": "Missing token in initial message."})
            await websocket.close()
            return

        # Step 2: Validate JWT and fetch user
        user = _get_user_from_token(token)
        if not user:
            await websocket.send_json({"step": "auth", "status": "error", "message": "Invalid or expired token."})
            await websocket.close()
            return

        # Step 3: Run the full scan
        await run_scan(mode=mode, user_id=user.id, websocket=websocket)

    except WebSocketDisconnect:
        logger.info("Client disconnected during scan.")
    except Exception as e:
        try:
            await websocket.send_json({"step": "unknown", "status": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

from fastapi import Depends, HTTPException
from auth.security import get_current_user
from scan.models import Analysis

@router.get("/api/scans")
def list_scans(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        scans = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).all()
        return [
            {
                "id": s.id,
                "mode": s.mode,
                "total_resources_scanned": s.total_resources_scanned,
                "total_issues_found": s.total_issues_found,
                "total_estimated_monthly_savings_usd": s.total_estimated_monthly_savings_usd,
                "created_at": s.created_at
            }
            for s in scans
        ]
    finally:
        db.close()

@router.get("/api/scans/{analysis_id}")
def get_scan(analysis_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        scan = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
            
        return {
            "id": scan.id,
            "mode": scan.mode,
            "total_resources_scanned": scan.total_resources_scanned,
            "total_issues_found": scan.total_issues_found,
            "total_estimated_monthly_savings_usd": scan.total_estimated_monthly_savings_usd,
            "created_at": scan.created_at,
            "findings": json.loads(scan.findings_json),
            "summary": json.loads(scan.summary_json)
        }
    finally:
        db.close()
