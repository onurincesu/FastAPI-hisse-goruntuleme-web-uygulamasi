from fastapi import FastAPI,Depends
from fastapi.responses import HTMLResponse
import models
from database import engine
from routers import hisse_görüntüle
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app=FastAPI()

models.Base.metadata.create_all(bind=engine)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
templates = Jinja2Templates(directory="templates")
app.include_router(hisse_görüntüle.router)
app.mount("/static",StaticFiles(directory="static"),name="static")