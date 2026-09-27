"""
Standalone Asynchronous WebSocket Test Client Script.
Connects to ws://localhost:8000/ws/risk, receives initial_risk_state, and prints live risk updates.
Matches Phase 36 of Master Prompt.
"""

import sys
import json
import asyncio
import logging

try:
    import websockets
except ImportError:
    import urllib.request
    print("Please install websockets package: pip install websockets")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [WS-CLIENT] %(message)s")
logger = logging.getLogger("ws_test_client")


async def listen_to_risk_updates(url: str = "ws://localhost:8000/ws/risk"):
    logger.info(f"Connecting to SATHI WebSocket server at {url}...")
    try:
        async with websockets.connect(url) as websocket:
            logger.info("Connected successfully to WebSocket server.")

            # 1. Receive initial_risk_state
            initial_data = await websocket.recv()
            logger.info(f"RECEIVED INITIAL STATE:\n{json.dumps(json.loads(initial_data), indent=2)}")

            # 2. Listen for live broadcasts
            logger.info("Listening for live risk updates...")
            while True:
                msg = await websocket.recv()
                parsed = json.loads(msg)
                logger.info(f"RECEIVED LIVE BROADCAST ({parsed.get('type')}):\n{json.dumps(parsed, indent=2)}")

    except Exception as err:
        logger.error(f"WebSocket client error: {err}")


if __name__ == "__main__":
    asyncio.run(listen_to_risk_updates())
