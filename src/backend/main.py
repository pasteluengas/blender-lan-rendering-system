from typing import Annotated
import socket
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, shutil, subprocess
from pathlib import Path
import add

app = FastAPI()
app.mount("/outputs", StaticFiles(directory="output/"), name="outputs")
app.mount("/static", StaticFiles(directory="static/"), name="static")


origins = [
    "http://localhost:3000",    # Common React port
    "http://localhost:5173",    # Common Vite/Vue/Svelte port
    "http://127.0.0.1:3000",    # Loopback IP variant
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],              # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allows all headers
)

@app.get("/")
async def read_root():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()

    
    
    return {"Working": "yeah", "Run website": f"http://{ip}:3000?ip={ip}"}

@app.post("/form")
def read_form(blender_version: Annotated[str, Form()], blender_render: Annotated[str, Form()], blender_file: UploadFile = File(...)):
    #cleaning dirs
    add.clearDir('uploads/')
    add.clearDir('output/')
    
    #subp_out = subprocess.run(["pwd"], capture_output=True, text=True)
    #saving file
    with open(f"uploads/{blender_file.filename}", "wb") as buffer:
        shutil.copyfileobj(blender_file.file, buffer)

    #rendering the scene
    blender_bin_param = "blender"
    match blender_version:
        case "2-82":
            blender_bin_param = "bin/2.82/blender"
        case "current":
            blender_bin_param = "blender"

    blender_render_param = "render_image"
    match blender_render:
        case "render_image":
            blender_render_param = ["-f", "1"]
        case "render_animation":
            blender_render_param = ["-a"]
            

    blender_file_param = f"uploads/{blender_file.filename}"

    #blender -b "/input/file.blend" -o "output/" -f 1
    command_param = [blender_bin_param, "-b", blender_file_param, "-o", "output/"]
    command_param.extend(blender_render_param)

    subp_out = subprocess.run(command_param, capture_output=True, text=True)
    print(subp_out.stdout.strip(), flush=True)

    tmp = " ".join(command_param)
    return {"blender_version": blender_version, "blender_file": blender_file.filename, "blender_render": blender_render, "command": tmp, "command_output": subp_out.stdout.strip()}

@app.get("/outputs")
async def listOutputFiles():
    files = {
        "folder": "outputs/",
        "file": []
    }
    
    for file_path in Path("output/").iterdir():
        files["file"].append({
            "name": file_path.name,
            "size": file_path.stat().st_size
        })

    return files

@app.get("/blender-versions")
async def listOutputFiles():
    files = {
        "version": []
    }
    
    for file_path in Path("bin/").iterdir():
        files["version"].append({
            "software": "blender",
            "version": file_path.name,
        })

    return files

@app.get("/server-info")
async def get_server_info():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return {"ip": ip}

    
"""
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
