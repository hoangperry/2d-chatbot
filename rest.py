import time
import uvicorn

from fastapi import FastAPI, File, Form
from fastapi import HTTPException, UploadFile, Request, Response, status
from fastapi.responses import JSONResponse
from pathlib import Path
from pydantic import BaseModel
from typing import List
from fastapi import Header
from fastapi import FastAPI
from fastapi import WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates("templates")
app = FastAPI(title="Demo REST Server")
CHUNK_SIZE = 1024*1024
video_path = Path("example.mp4")


class Item(BaseModel):
    name: str
    price: float
    quantity: int


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def home(request: Request):
    template = "index.html"
    context = {"request": request, 'client_id': str(time.time()).replace('.', '')}
    return templates.TemplateResponse(template, context)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@app.get("/video")
async def video_endpoint(range: str = Header(None)):
    start, end = range.replace("bytes=", "").split("-")
    video_path = Path('example.mp4')
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")


if __name__ == '__main__':
    uvicorn.run("rest:app", host='0.0.0.0', port=5000, reload=True, debug=True, workers=3)
