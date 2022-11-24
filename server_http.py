import os
import time
import uvicorn

from config.config import dialogflow_config
from helper.utils import id_generator
from chatbot.management import SessionManagement
from chatbot.session import GoogleDialogflowSession
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
session_manager = SessionManagement()


@app.get("/health_check")
async def root():
    return {"message": "Hello World"}


@app.post("/audio")
async def gen_audio(request: Request):
    st_time = time.time()
    req = await request.json()
    requested_text = req.get("text", "")
    cb_session_id = req.get("id", "")

    this_session = session_manager.get(cb_session_id, None)
    if this_session is None:
        this_session = GoogleDialogflowSession(dialogflow_config)
        session_manager[cb_session_id] = this_session
    chat_bot_st_time = time.time()
    cb_response = this_session.chat(text=requested_text)
    chat_bot_st_time = time.time() - chat_bot_st_time

    audio, visemes, tts_visemes_ex_time = generate_audio_and_visemes(cb_response)
    if visemes is None:
        visemes = dict()

    # Transform Visemes
    visemes = [[i['start'], i['value']] for i in visemes['mouthCues']]
    print(f'Responded in {time.time() - st_time}')
    return {
        'time_process': {
            'total': time.time() - st_time,
            'chatbot': chat_bot_st_time,
            'tts': tts_visemes_ex_time[0],
            'visemes': tts_visemes_ex_time[1],
        },
        'text': cb_response,
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
        {"request": request, 'session_id': id_generator()},
    )


if __name__ == '__main__':
    uvicorn.run("server_http:app", host="0.0.0.0", port=8000, reload=True)
