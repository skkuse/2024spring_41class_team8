import os
import re
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import threading
from java_execution import compile_and_run_java_code
from carbon_emission import calculate_carbon_emissions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용
)

# Static files 서빙 설정
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    with open(os.path.join("../frontend", "code_test.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)

class Code(BaseModel):
    java_code: str

@app.post("/submit")
async def receive_code(code: Code):
    result = compile_and_run_java_code(code.java_code)
    
    if "error" in result:
        os.remove(result["java_file_path"])
        if os.path.exists(f"{result['class_name']}.class"):
            os.remove(f"{result['class_name']}.class")
        raise HTTPException(status_code=400, detail=result["error"])

    execution_time = result["execution_time"]
    memory_usage = result["memory_usage"]

    # 탄소 배출량 계산
    carbon_emissions = calculate_carbon_emissions(execution_time)

    # 임시 파일 삭제
    os.remove(result["java_file_path"])
    os.remove(f"{result['class_name']}.class")

    return {
        "java_code": code.java_code,
        "execution_time": execution_time,
        "memory_usage": memory_usage ,  # Convert to MB
        "carbon_emissions": carbon_emissions,
        "output": result["stdout"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
