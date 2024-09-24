from fastapi import UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from fastapi import APIRouter
from pathlib import Path

DATA_DIR = "/data"
DATA_DIR_PATH = Path(DATA_DIR)
DATA_DIR_PATH.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.post("/data/{filename:path}")
async def upload_file(filename: str, body: bytes = File(...)):
    file_location = DATA_DIR_PATH / filename
    os.makedirs("/".join(str(file_location).split("/")[:-1]), exist_ok=True)    
    with open(file_location, "wb") as f:
        f.write(body)
    return {"info": f"file saved at '{file_location}'"}


@router.get("/data/{filename:path}")
async def get_file(filename: str):
    file_location = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location)