import uvicorn
from os.path import getsize
from pathlib import Path
from typing import Generator
from fastapi import FastAPI, status, HTTPException
from fastapi import Request, Response
from fastapi import Header
from fastapi.templating import Jinja2Templates
from starlette.responses import StreamingResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
CHUNK_SIZE = 1024 * 1024
video_path = 'ex.mp4'


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


def get_data_from_file(file_path: str) -> Generator:
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()


@app.get("/video")
async def video_endpoint():
    content_path = 'ex.mp4'

    def iterfile():
        with open(content_path, mode="rb") as file_like:  #
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")


if __name__ == '__main__':
    uvicorn.run("server_transcript:app", host='0.0.0.0', port=8000, reload=True, debug=True, workers=3)
