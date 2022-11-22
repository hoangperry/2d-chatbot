import uvicorn


from pathlib import Path
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

app = FastAPI()

TEMPLATES = Jinja2Templates(directory=str("html/http"))


@app.get("/health_check")
async def root():
    return {"message": "Hello World"}


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
