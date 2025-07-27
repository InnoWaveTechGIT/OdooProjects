import asyncio
import websockets
import threading
import json

class WebSocketServer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.clients = set()
            cls._instance.server = None
        return cls._instance

    async def handler(self, websocket):
        self.clients.add(websocket)
        try:
            async for _ in websocket:
                pass  # Keep connection alive
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, data):
        if self.clients:
            message = json.dumps(data)
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )

    def start(self):
        async def server_main():
            async with websockets.serve(
                self.handler,
                "0.0.0.0",
                8765
            ):
                print("WebSocket server started on port 8765")
                await asyncio.Future()  # Run forever

        # Create new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server_main())

def start_websocket_thread():
    server = WebSocketServer()
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    return thread
