import asyncio
from typing import List

class BroadcastLogger:
    def __init__(self):
        self.active_connections: List[asyncio.Queue] = []

    def register_client(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.active_connections.append(queue)
        return queue

    def unregister_client(self, queue: asyncio.Queue):
        if queue in self.active_connections:
            self.active_connections.remove(queue)

    async def log(self, message: str):
        # Keeps standard local terminal printing working
        print(message)
        # Simultaneously broadcasts to the browser UI via WebSocket queues
        for queue in self.active_connections:
            await queue.put(message)

# Global singleton instance shared across main.py and server.py
ws_logger = BroadcastLogger()
