import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from runner.main import start_pipeline
from runner.logger import ws_logger

app = FastAPI(title="RT-SANDBOX Web Endpoint Gateway")

# Ensure your report workspace paths exist cleanly on disk layout
os.makedirs("reports", exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard_root():
    """Serves the main application control dashboard interface."""
    index_path = os.path.join("runner", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/run")
async def trigger_sandbox_pipeline():
    """Spawns the test orchestrator sequence as a decoupled background loop task."""
    # Execute loop concurrently inside active asyncio worker context
    asyncio.create_task(start_pipeline())
    return {"status": "processing", "message": "Pipeline worker spawned successfully"}

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """Binds live browser sessions directly into your pipeline execution queue logs."""
    await websocket.accept()
    log_queue = ws_logger.register_client()
    try:
        while True:
            # Non-blocking pull from your custom global async logger queue
            log_message = await log_queue.get()
            await websocket.send_text(log_message)
            log_queue.task_done()
    except WebSocketDisconnect:
        pass
    finally:
        ws_logger.unregister_client(log_queue)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("runner.server:app", host="127.0.0.1", port=8000, reload=True)