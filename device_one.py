import asyncio
import json
import random
import websockets

WS_URL = "ws://127.0.0.1:8000/ws"

async def run():
    async with websockets.connect(WS_URL) as ws:
        # Receive initial hello
        hello = await ws.recv()
        print("[device_one] server hello:", hello)

        for i in range(10):
            value = round(random.uniform(20.0, 30.0), 2)
            msg = {"type": "telemetry", "device_id": "device_one", "value": value}
            await ws.send(json.dumps(msg))
            print("[device_one] sent telemetry:", msg)

            # Listen for one broadcast (optional)
            broadcast = await ws.recv()
            print("[device_one] received:", broadcast)

            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
