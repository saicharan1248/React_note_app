from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# LLM Configuration (OpenAI)
openai.api_key = "your_openai_api_key"

# Database Setup
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    summary = Column(String)

Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Request Models
class NoteRequest(BaseModel):
    content: str

# Routes
@app.post("/add_note/")
async def add_note(request: NoteRequest):
    # Summarize the note with OpenAI
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this note: {request.content}",
            max_tokens=50
        )
        summary = response.choices[0].text.strip()

        # Save to database
        db = SessionLocal()
        note = Note(content=request.content, summary=summary)
        db.add(note)
        db.commit()
        db.refresh(note)
        db.close()

        return {"id": note.id, "content": note.content, "summary": note.summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_notes/")
async def get_notes():
    db = SessionLocal()
    notes = db.query(Note).all()
    db.close()
    return notes
