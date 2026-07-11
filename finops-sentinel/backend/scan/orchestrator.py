import json
import logging
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from aws_fetcher.fetcher import fetch_all_resources
from analysis.analyzer import analyze_resources

logger = logging.getLogger(__name__)


from auth.database import SessionLocal
from scan.models import Analysis
from aws_fetcher.live_source import AWSFetchError
from analysis.gemini_client import GeminiAnalysisError

def get_user_friendly_error_message(e: Exception) -> str:
    """Maps internal exceptions to clean, human-readable messages for the frontend."""
    if isinstance(e, AWSFetchError):
        return "Failed to fetch AWS resource data. Please check your AWS credentials and try again."
    elif isinstance(e, GeminiAnalysisError):
        return str(e) # Already clean from the client
    else:
        return "Something went wrong during the scan. Please try again."

def save_analysis_result(user_id: int, mode: str, result: dict) -> int:
    """
    Saves the analysis result into the SQLite database.
    """
    summary = result.get("summary", {})
    findings = result.get("findings", [])
    
    db = SessionLocal()
    try:
        new_analysis = Analysis(
            user_id=user_id,
            mode=mode,
            findings_json=json.dumps(findings),
            summary_json=json.dumps(summary),
            total_resources_scanned=summary.get("total_resources_scanned", 0),
            total_issues_found=summary.get("total_issues_found", 0),
            total_estimated_monthly_savings_usd=summary.get("total_estimated_monthly_savings_usd", 0.0)
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        logger.info(f"Saved analysis {new_analysis.id} for user {user_id}")
        return new_analysis.id
    finally:
        db.close()


def _count_resources(resource_data: dict) -> int:
    """Count total number of resources across all resource types."""
    total = 0
    # EC2 instances (nested in Reservations)
    for res in resource_data.get("ec2_instances", {}).get("Reservations", []):
        total += len(res.get("Instances", []))
    total += len(resource_data.get("ebs_volumes", {}).get("Volumes", []))
    total += len(resource_data.get("elastic_ips", {}).get("Addresses", []))
    total += len(resource_data.get("rds_instances", {}).get("DBInstances", []))
    total += len(resource_data.get("load_balancers", {}).get("LoadBalancers", []))
    total += len(resource_data.get("s3_buckets", {}).get("Buckets", []))
    # Metrics are per-instance, don't double count
    return total


async def _safe_send(websocket: WebSocket, payload: dict) -> bool:
    try:
        await websocket.send_json(payload)
        return True
    except WebSocketDisconnect:
        logger.info("Client disconnected during scan (WebSocketDisconnect). Stopping flow.")
        return False
    except Exception as e:
        logger.info(f"Client disconnected or socket error during scan: {e}. Stopping flow.")
        return False


async def run_scan(mode: str, user_id: int, websocket: WebSocket):
    """
    Orchestrates the full scan flow:
    1. Fetch AWS resources
    2. Analyze with Gemini
    3. Save result (placeholder)
    4. Send final result over WebSocket
    """
    current_step = "fetching_resources"
    resource_data = None
    analysis_result = None

    try:
        # Step 1: Fetch resources
        if not await _safe_send(websocket, {"step": "fetching_resources", "status": "in_progress"}): return
        resource_data = await asyncio.to_thread(fetch_all_resources, mode)
        resource_count = _count_resources(resource_data)
        if not await _safe_send(websocket, {
            "step": "fetching_resources",
            "status": "done",
            "resource_count": resource_count
        }): return

        # Step 2: Analyze with Gemini
        current_step = "analyzing"
        if not await _safe_send(websocket, {"step": "analyzing", "status": "in_progress"}): return
        analysis_result = await asyncio.to_thread(analyze_resources, resource_data)
        if not await _safe_send(websocket, {"step": "analyzing", "status": "done"}): return

        # Step 3: Save result (placeholder)
        current_step = "saving"
        if not await _safe_send(websocket, {"step": "saving", "status": "in_progress"}): return
        analysis_id = save_analysis_result(user_id, mode, analysis_result)
        if not await _safe_send(websocket, {"step": "saving", "status": "done"}): return

        # Step 4: Send final result
        await _safe_send(websocket, {
            "step": "complete",
            "status": "success",
            "result": analysis_result,
            "analysis_id": analysis_id
        })

    except Exception as e:
        logger.exception(f"Scan failed at step '{current_step}': {e}")
        clean_msg = get_user_friendly_error_message(e)
        await _safe_send(websocket, {
            "step": current_step,
            "status": "error",
            "message": clean_msg
        })
