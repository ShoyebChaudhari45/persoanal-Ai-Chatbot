from fastapi import FastAPI, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from db import init_db, SessionLocal, QAMemory
from langchain_google_genai import ChatGoogleGenerativeAI
# from deepface import DeepFace
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

app = FastAPI(title="Shoyeb AI Portfolio Assistant")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


PROFILE_CONTEXT = """
You are an AI portfolio assistant representing **Shoyeb ShaikhChand Chaudhari**.
You ALWAYS answer in **third person only (he / him / Shoyeb)**.
You must use **formatted responses** — headings, bullet points, bold keywords — with slight humour.
If information is not available, reply **exactly**: "I don't know."

-----------------------------------------
PROFILE
-----------------------------------------
Name: Shoyeb ShaikhChand Chaudhari
Role: Android & Software Developer
Email: chaudharishoyeb@gmail.com
GitHub: github.com/ShoyebChaudhari45
LinkedIn: linkedin.com/in/shoyeb-chaudhari1
Open to work.

-----------------------------------------
SKILLS
-----------------------------------------
Java, Python, SQL, PHP
Android SDK, Firebase, Retrofit, XML UI, RecyclerView
Flask REST APIs, HTML, CSS, JavaScript
PyTorch, Scikit-learn, DeepFace
MySQL, Firestore, MongoDB

-----------------------------------------
PROJECTS
-----------------------------------------
• CropGuard – AI Crop Disease Detector
• Safario – Trip Planner App
• CampusCircle – College Community App
• SMS Spam Detection App
• Hospital & Blood Donor Finder
• Dream House 3D Plan Generator
• Web-based Face Recognition Voting System

-----------------------------------------
EXPERIENCE
-----------------------------------------
Software Developer Intern — Mountreach Solutions (Jun 2025 – Present)

-----------------------------------------
EDUCATION
-----------------------------------------
B.Tech CSE — CGPA 7.65
Diploma — 83.77%
SSC — 90%

-----------------------------------------
RESPONSE STYLE RULES
-----------------------------------------
• 3rd person only
• Premium formatting
• Slight humour allowed (not cringe)
• If unknown → "I don't know."
"""

class Ask(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask")
async def ask(req: Ask, db: Session = Depends(get_db)):
    llm = ChatGoogleGenerativeAI(model=MODEL, api_key=API_KEY)
    prompt = PROFILE_CONTEXT + "\n\nUSER QUESTION: " + req.question
    res = llm.invoke(prompt)
    answer = res.content

    db.add(QAMemory(question=req.question, answer=answer))
    db.commit()

    return {"answer": answer}


# @app.post("/verify-photo")
# async def verify_photo(file: UploadFile = File(...)):
    uploaded = "temp.jpg"
    reference = "shoyeb.jpg"   # your real stored photo

    with open(uploaded, "wb") as f:
        f.write(await file.read())

    try:
        result = DeepFace.verify(uploaded, reference, model_name="Facenet")
        if result["verified"]:
            return {"match": True, "message": "🔥 Yes! Yeh photo Shoyeb ka hi hai — handsome banda 😎"}
        return {"match": False, "message": "❌ Nope bhai — yeh Shoyeb nahi lag raha 😂"}
    except:
        return {"match": False, "message": "⚠ Face detect nahi ho paaya — clearer image try karo."}
