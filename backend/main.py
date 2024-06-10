import os
import re
import time
import subprocess
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from fastapi.templating import Jinja2Templates
import logging
import urllib.parse
from java_execution import compile_and_run_java_code
from carbon_emission import calculate_carbon_emissions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 인증 정보 설정
cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 생성
db = firestore.client()

# Static files 서빙 설정
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
app.mount("/community/static", StaticFiles(directory="../frontend/community"), name="community")

# 템플릿 설정
templates = Jinja2Templates(directory="../frontend/community")

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

def get_client_ip(request: Request) -> str:
    return request.client.host

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    with open(os.path.join("../frontend/community", "main_page.html"), encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)

class Code(BaseModel):
    java_code: str

def fix_code(input_code: str) -> str:
    sourcepath = "src"
    buggy_file_path = os.path.join(sourcepath, "Buggy.java")
    fixed_file_path = os.path.join(sourcepath, "Fixed.java")

    with open(buggy_file_path, "w") as f:
        f.write(input_code)

    compile_cmd = ["javac", os.path.join(sourcepath, "Main.java")]
    run_cmd = ["java", "-cp", sourcepath, "Main"]

    try:
        subprocess.run(compile_cmd, check=True)
        subprocess.run(run_cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Java execution error: {str(e)}")

    with open(fixed_file_path, "r") as f:
        fixed_code = f.read()

    os.remove(buggy_file_path)
    os.remove(fixed_file_path)
    class_file = os.path.join(sourcepath, "Main.class")
    if os.path.exists(class_file):
        os.remove(class_file)

    return fixed_code

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

    carbon_emissions = calculate_carbon_emissions(execution_time, memory_usage)

    os.remove(result["java_file_path"])
    os.remove(f"{result['class_name']}.class")

    fixed_code = fix_code(code.java_code)

    result_after_fixed = compile_and_run_java_code(fixed_code)

    after_excution_time = result_after_fixed["execution_time"]
    after_memory_usage = result_after_fixed["memory_usage"]

    after_carbon_emissions = calculate_carbon_emissions(after_excution_time, after_memory_usage)

    reduced_emissions = (1 - after_carbon_emissions / carbon_emissions) * 100

    os.remove(result_after_fixed["java_file_path"])
    os.remove(f"{result_after_fixed['class_name']}.class")
    return {
        "java_code": code.java_code,
        "execution_time": execution_time,
        "memory_usage": memory_usage,
        "carbon_emissions": carbon_emissions,
        "output": fixed_code,
        "fixed_execution_time": after_excution_time,
        "fixed_memory_usage": after_memory_usage,
        "fixed_carbon_emissions": after_carbon_emissions,
        "reduced_emmisions": reduced_emissions
    }

@app.get("/community", response_class=HTMLResponse)
async def read_community(request: Request):
    posts_ref = db.collection('ecomaster_community').order_by('postnumber')
    docs = posts_ref.stream()

    posts = []
    for doc in docs:
        post_data = doc.to_dict()
        if 'postdate' in post_data:
            try:
                postdate_str = post_data['postdate'].strftime('%Y-%m-%d %H:%M:%S')
                post_data['postdate'] = postdate_str
            except Exception as e:
                logging.error(f"Date format error: {e}")
                post_data['postdate'] = "Invalid date format"
        post_data['id'] = doc.id
        logging.debug(f"Post data: {post_data}")
        posts.append(post_data)

    logging.debug(f"Posts: {posts}")
    return templates.TemplateResponse("community.html", {"request": request, "posts": posts})

@app.get("/community/suggested", response_class=HTMLResponse)
async def read_suggested_community(request: Request):
    posts_ref = db.collection('ecomaster_community').where('suggest', '>=', 10).order_by('suggest', direction=firestore.Query.DESCENDING)
    docs = posts_ref.stream()

    posts = []
    for doc in docs:
        post_data = doc.to_dict()
        if 'postdate' in post_data:
            try:
                postdate_str = post_data['postdate'].strftime('%Y-%m-%d %H:%M:%S')
                post_data['postdate'] = postdate_str
            except Exception as e:
                logging.error(f"Date format error: {e}")
                post_data['postdate'] = "Invalid date format"
        post_data['id'] = doc.id
        logging.debug(f"Post data: {post_data}")
        posts.append(post_data)

    logging.debug(f"Posts: {posts}")
    return templates.TemplateResponse("community.html", {"request": request, "posts": posts})

@app.get("/community/category/{category_name}", response_class=HTMLResponse)
async def read_category_community(request: Request, category_name: str):
    logging.debug(f"Fetching posts for category: {category_name}")
    
    try:
        posts_ref = db.collection('ecomaster_community').where('category', '==', category_name)
        docs = posts_ref.stream()
    except Exception as e:
        logging.error(f"Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching posts from Firestore")

    posts = []
    for doc in docs:
        post_data = doc.to_dict()
        if 'postdate' in post_data:
            try:
                postdate_str = post_data['postdate'].strftime('%Y-%m-%d %H:%M:%S')
                post_data['postdate'] = postdate_str
            except Exception as e:
                logging.error(f"Date format error: {e}")
                post_data['postdate'] = "Invalid date format"
        post_data['id'] = doc.id
        posts.append(post_data)
    
    logging.debug(f"Fetched posts: {posts}")

    return templates.TemplateResponse("community.html", {"request": request, "posts": posts})

@app.get("/write", response_class=HTMLResponse)
async def write_post(request: Request):
    return templates.TemplateResponse("write_post.html", {"request": request})

@app.post("/submit_post")
async def submit_post(request: Request, title: str = Form(...), category: str = Form(...), content: str = Form(...), password: str = Form(...)):
    postnumber_ref = db.collection('ecomaster_community').order_by('postnumber', direction=firestore.Query.DESCENDING).limit(1)
    postnumber_docs = postnumber_ref.stream()
    postnumber = 1
    for doc in postnumber_docs:
        postnumber = doc.to_dict().get('postnumber', 0) + 1

    client_host = request.client.host
    new_post_ref = db.collection('ecomaster_community').add({
        'postnumber': postnumber,
        'category': category,
        'title': title,
        'detail': content,
        'postdate': datetime.now(),
        'views': 0,
        'comments': [],
        'suggest': 0,
        "password": password,
        "writerIP": client_host
    })

    post_id = new_post_ref[1].id
    logging.debug(f"Generated post_id: {post_id}")

    return RedirectResponse(url=f'/post/{post_id}', status_code=303)

@app.get("/post/{post_id}", response_class=HTMLResponse)
async def read_post(request: Request, post_id: str):
    logging.debug(f"Received post_id: {post_id}")
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.to_dict()
    post_data['id'] = post_id
    if 'postdate' in post_data:
        try:
            postdate_str = post_data['postdate'].strftime('%Y-%m-%d %H:%M:%S')
            post_data['postdate'] = postdate_str
        except Exception as e:
            logging.error(f"Date format error: {e}")
            post_data['postdate'] = "Invalid date format"
    post_ref.update({"views": post_data.get("views", 0) + 1})
    post_data['views'] += 1

    comments = post_data.get('comments', [])

    return templates.TemplateResponse("post_detail.html", {"request": request, "post": post_data, "comments": comments})

@app.post("/post/{post_id}/comments")
async def add_comment(post_id: str, comment: str = Form(...)):
    logging.debug(f"Received post_id: {post_id}")
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.to_dict()

    comments = post_data.get('comments', [])
    comments.append({"content": comment, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    post_ref.update({"comments": comments})

    return RedirectResponse(url=f'/post/{post_id}', status_code=303)

@app.post("/post/{post_id}/suggest")
async def suggest_post(request: Request, post_id: str):
    client_ip = get_client_ip(request)
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_data = post.to_dict()
    
    if "suggest_ip" not in post_data or not isinstance(post_data["suggest_ip"], list):
        post_data["suggest_ip"] = []

    if client_ip in post_data["suggest_ip"]:
        raise HTTPException(status_code=400, detail="You have already suggested this post.")
    
    post_ref.update({
        "suggest": firestore.Increment(1),
        "suggest_ip": firestore.ArrayUnion([client_ip])
    })
    
    updated_post = post_ref.get()
    updated_suggest = updated_post.to_dict().get("suggest", 0)
    
    logging.debug(f"Updated suggest count: {updated_suggest}")

    return JSONResponse(content={"message": "Post suggested successfully", "suggest": updated_suggest})

@app.post("/post/{post_id}/check_password")
async def check_password(post_id: str, data: dict):
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.to_dict()
    detail = post_data.get('detail', '')
    encoded_detail = urllib.parse.quote(detail) if detail is not None else ''
    if post_data.get('password') == data.get('password'):
        return {"message": "Password is correct", "post": {
            "title": post_data.get('title'),
            "category": post_data.get('category'),
            "detail": encoded_detail
        }}
    else:
        raise HTTPException(status_code=400, detail="Incorrect password")

@app.get("/modify_post")
async def get_modify_post(request: Request, postnumber: str, title: str, category: str, content: str, password: str):
    return templates.TemplateResponse("modify_post.html", {"request": request, "postnumber": postnumber, "title": title, "category": category, "content": content, "password": password})

@app.post("/modify_post")
async def modify_post(request: Request, postnumber: str = Form(...), title: str = Form(...), category: str = Form(...), detail: str = Form(...), password: str = Form(...), new_password: str = Form(...)):
    post_ref = db.collection('ecomaster_community').document(postnumber)
    post = post_ref.get()
    if not post.exists:
        return JSONResponse(content={"message": "Post not found"}, status_code=404)
    post_data = post.to_dict()
    if post_data['password'] == password:
        post_ref.update({
            "title": title,
            "category": category,
            "detail": detail,
            "password": new_password
        })
        # return JSONResponse(content={"message": "Post modified successfully"})
        return RedirectResponse(url="/community", status_code=303)
    else:
        return JSONResponse(content={"message": "Incorrect password"}, status_code=401)

@app.get("/modify_post/{post_id}")
async def get_modify_post_page(request: Request, post_id: str, password: str):
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.to_dict()
    if post_data.get('password') == password:
        return templates.TemplateResponse("modify_post.html", {"request": request, "postnumber": post_id, "title": post_data['title'], "category": post_data['category'], "content": post_data['detail'], "password": password})
    else:
        raise HTTPException(status_code=400, detail="Incorrect password")

@app.post("/update_post/{post_id}")
async def update_post(request: Request, post_id: str, title: str = Form(...), category: str = Form(...), content: str = Form(...), password: str = Form(...)):
    post_ref = db.collection('ecomaster_community').document(post_id)
    post = post_ref.get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.to_dict()
    if post_data.get("password") != password:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    post_ref.update({
        "title": title,
        "category": category,
        "detail": content,
        "password": password
    })
    return RedirectResponse(url='/community', status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
