from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .security import create_access_token, get_current_user, hash_password, verify_password

Base.metadata.create_all(bind=engine)  # fine for a demo; use Alembic migrations in production

app = FastAPI(title="Secure Notes API", version="0.1.0")


@app.get("/health", tags=["ops"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.UserOut, status_code=201, tags=["auth"])
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.User).where(models.User.email == payload.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = models.User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token, tags=["auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return schemas.Token(access_token=create_access_token(user.id))


@app.post("/notes", response_model=schemas.NoteOut, status_code=201, tags=["notes"])
def create_note(
    payload: schemas.NoteCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    note = models.Note(**payload.model_dump(), owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/notes", response_model=list[schemas.NoteOut], tags=["notes"])
def list_notes(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.scalars(select(models.Note).where(models.Note.owner_id == user.id)).all()


@app.get("/notes/{note_id}", response_model=schemas.NoteOut, tags=["notes"])
def get_note(note_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = db.get(models.Note, note_id)
    if note is None or note.owner_id != user.id:  # 404 for other users' notes: don't leak existence
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@app.delete("/notes/{note_id}", status_code=204, tags=["notes"])
def delete_note(note_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = db.get(models.Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    db.delete(note)
    db.commit()
