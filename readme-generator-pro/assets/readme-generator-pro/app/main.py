from fastapi import FastAPI,Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import router

app = FastAPI(title="README Generator Pro")
app.include_router(router, prefix="/api")

# 基于当前文件位置动态构建静态文件目录的绝对路径
# Path(__file__).resolve() 获取当前文件(main.py)的绝对路径
# .parent 获取当前文件所在目录(/mnt/workspace/readme_skills/app/)
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"  # 拼接static目录路径

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)