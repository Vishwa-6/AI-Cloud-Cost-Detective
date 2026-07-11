"""
WebSocket Test Client for FinOps Sentinel Scan Endpoint
--------------------------------------------------------
Usage:
  1. Make sure the backend is running:
       uvicorn main:app --reload

  2. First, get a JWT token by signing up and logging in:
       Sign up (only needed once):
         curl -X POST http://localhost:8000/api/auth/signup \
           -H "Content-Type: application/json" \
           -d '{"email": "test@example.com", "password": "testpassword"}'

       Login to get a token:
         curl -X POST http://localhost:8000/api/auth/login \
           -H "Content-Type: application/json" \
           -d '{"email": "test@example.com", "password": "testpassword"}'
       
       Copy the "access_token" value from the response.

  3. Set your token below (or pass via environment variable) and run this script:
       set FINOPS_TOKEN=your_jwt_token_here
       python scan/test_ws_client.py
"""

import asyncio
import json
import os
import websockets

# --- CONFIGURE THESE ---
WS_URL = "ws://localhost:8000/api/scan/ws"
TOKEN = os.environ.get("FINOPS_TOKEN", "PASTE_YOUR_JWT_TOKEN_HERE")
MODE = "mock"
# -----------------------

if TOKEN == "PASTE_YOUR_JWT_TOKEN_HERE":
    print("⚠️  WARNING: No token configured.")
    print("   Set the FINOPS_TOKEN environment variable or edit this file.")
    print("   Example: set FINOPS_TOKEN=eyJhbGci...")
    print()


async def run():
    print(f"Connecting to {WS_URL}...")
    async with websockets.connect(WS_URL) as ws:
        # Send auth + mode message
        init_msg = json.dumps({"mode": MODE, "token": TOKEN})
        await ws.send(init_msg)
        print(f"Sent: {init_msg}\n")
        print("--- Receiving messages ---")

        while True:
            try:
                raw = await ws.recv()
                msg = json.loads(raw)
                print(json.dumps(msg, indent=2))

                # Stop when we receive a terminal message
                if msg.get("step") in ("complete", "error", "auth") and msg.get("status") in ("success", "error"):
                    break
            except websockets.ConnectionClosed:
                print("\n[Connection closed by server]")
                break

    print("\n--- Scan complete ---")


if __name__ == "__main__":
    asyncio.run(run())
