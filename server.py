import os
import websockets
import asyncio

connected = set()


async def server(websocket, path):
    # Register.
    connected.add(websocket)
    try:
        async for data in websocket:
            for conn in connected:
                await conn.send(data)
    finally:
        # Unregister.
        connected.remove(websocket)


start_server = websockets.serve(server, "", int(os.environ.get("PORT", 5000)))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
