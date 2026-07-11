from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import UserSignup, UserLogin, UserResponse, Token
from .security import get_password_hash, verify_password, create_access_token, get_current_user
from limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
@limiter.limit("5/minute")
def signup(request: Request, user_data: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Invalid request")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise generic_error
        
    if not verify_password(user_data.password, user.hashed_password):
        raise generic_error
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
