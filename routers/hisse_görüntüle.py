import json
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
import models
from database import Sessionlocal
from fastapi.responses import HTMLResponse, JSONResponse
import yfinance as yf
import pandas as pd
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from typing import List
import asyncio

router = APIRouter(
    prefix="/hisseler",
    tags=["hisseler"],
    responses={404: {"description": "Not found"}}
)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

with open("hisseler.json", "r", encoding="utf-8") as json_file:
    hisseler = json.load(json_file)

async def hisseleri_getir(db: db_dependency):
    tasks = []
    for hisse, isimler in hisseler.items():
        check = db.query(models.hisseler).filter_by(kod=hisse).first()
        if check:
            stock = yf.Ticker(hisse)
            data = stock.history(period="1d")
            latest_price = round(data["Close"].iloc[-1], 2)
            latest_volume = stock.info["volume"]
            check.fiyat = latest_price
            check.hacim = latest_volume
            check.ad = isimler
            db.commit()
        else:
            stock = yf.Ticker(hisse)
            data = stock.history(period="1d")
            latest_price = round(data["Close"].iloc[-1], 2)
            latest_volume = stock.info["volume"]
            yeni_hisse = models.hisseler(kod=hisse, fiyat=latest_price, hacim=latest_volume)
            db.add(yeni_hisse)
            db.commit()
        tasks.append(asyncio.create_task(asyncio.sleep(0)))
    await asyncio.gather(*tasks)

templates = Jinja2Templates(directory="templates")

@router.post("/")
async def guncelle(db: db_dependency):
    await hisseleri_getir(db)
    return {"basarili": True}

@router.get("/sonuc")
async def tum_hisseler(request: Request, db: db_dependency) -> HTMLResponse:
    veriler = db.query(models.hisseler).order_by("id").all()
    if veriler:
        return templates.TemplateResponse("hisseler.html", {"request": request, "veriler": veriler})
    else:
        raise HTTPException(status_code=404, detail="Not found")

@router.get("/hisse/{kod}", response_class=HTMLResponse)
async def hisse_detay(request: Request, kod: str, db: db_dependency) -> HTMLResponse:
    sonuc = db.query(models.hisseler).filter_by(kod=kod).first()
    if not sonuc:
        raise HTTPException(status_code=404, detail="Kod bulunamadi.")
    return templates.TemplateResponse("hisse.html", {"request": request, "kod": kod, "fiyat": sonuc.fiyat, "hacim": sonuc.hacim})
