from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS (разрешаем доступ с фронта)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/transactions", response_model=schemas.Transaction)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_tx = models.Transaction(**tx.dict())
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@app.get("/transactions", response_model=list[schemas.Transaction])
def read_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()

@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pw = hash_password(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.UserOut)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные")
    return db_user


@app.post("/blog-posts", response_model=schemas.BlogPost)
def create_blog_post(post: schemas.BlogPostCreate, db: Session = Depends(get_db)):
    db_post = models.BlogPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/blog-posts", response_model=list[schemas.BlogPost])
def read_blog_posts(db: Session = Depends(get_db)):
    return db.query(models.BlogPost).order_by(models.BlogPost.id.desc()).all()
