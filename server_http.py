import os
import time
import uvicorn

from engine.speech import generate_audio_and_visemes, np_to_base64

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request

from starlette.templating import _TemplateResponse

app = FastAPI()
root = os.path.dirname(os.path.abspath(__file__))

TEMPLATES = Jinja2Templates(directory=str("html/http"))

app.mount("/js", StaticFiles(directory=os.path.join(root, 'html/http')), name="js")
app.mount("/character", StaticFiles(directory=os.path.join(root, 'character/morty')), name="js")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health_check")
async def root():
    return {"message": "Hello World"}


@app.post("/audio")
def gen_audio(text: str):
    st_time = time.time()
    audio, visemes = generate_audio_and_visemes(text)
    if visemes is None:
        visemes = dict()

    # Transform Visemes
    visemes = [[i['start'], i['value']] for i in visemes['mouthCues']]
    print(f'Responded in {time.time() - st_time}')
    return {
        'time_process': time.time() - st_time,
        'text': text,
        'visemes': visemes,
        'audio': np_to_base64(audio),
    }


@app.get("/", status_code=200)
def root(request: Request) -> _TemplateResponse:
    """
    Root GET
    """
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request},
    )


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
