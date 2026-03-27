from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/")
def ui_home() -> FileResponse:
    ui_file = Path(__file__).resolve().parents[2] / "ui" / "index.html"
    return FileResponse(path=ui_file)
