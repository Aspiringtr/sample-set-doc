import os
from pathlib import Path 
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Depends

import jwt
from pwdlib import PasswordHash

from sqlalchemy import select 
from sqlalchemy.orm import Session

from data_base.database import get_db,Base,engine
from auth.model import User


app = FastAPI(title="auth survice")

password_hash = PasswordHash.recommended()

########################
# GETTING ENV VARIABLE #
########################

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JWT_ACCESS_TOKEN_TIME = float(os.environ.get("JWT_ACCESS_TOKEN_TIME_MIN"))
JWT_REFRESH_TOKEN_TIME = float(os.environ.get("JWT_REFRESH_TOKEN_TIME_DAYS"))
JWT_KEY = os.environ.get("JWT_KEY")
JWT_ALGO = os.environ.get("JWT_ALGO")


###########################
# PYDANTIC DATA STRUCTURE #
###########################

class register_request(BaseModel):
    user_name: str = Field(min_length=3,max_length=50)
    user_password: str = Field(min_length=8, max_length=50)

class login_request(BaseModel):
    user_name:str
    user_password:str

class refresh_request(BaseModel):
    refresh_token:str

########################
# JWT CREATER / VERIFY #
########################

def create_jwt_token(user:str,role:str,token_type:str="access_token") -> str:

    try:
        current_time = datetime.now(timezone.utc)

        if (token_type == "access_token"):
            expire = current_time + timedelta(minutes=JWT_ACCESS_TOKEN_TIME)
        else:
            expire = current_time + timedelta(days=JWT_REFRESH_TOKEN_TIME)
            
        payload = {
            "user_name": user,
            "user_role": role,
            "token_type":token_type,
            "token_issued_time": current_time.timestamp(),
            "token_expiry_time":expire.timestamp()
        }

        token = jwt.encode(payload,key=JWT_KEY,algorithm=JWT_ALGO)

    except Exception as e:
        print (f"Error occured during token generation:{e}")

    return token

def jwt_decoder(token:str) -> dict:
    try:
        decoded_data = jwt.decode(jwt=token,key=JWT_KEY,algorithms=JWT_ALGO)

        if decoded_data.get("token_type") != 'refresh_token':
            raise HTTPException(
                status_code=401,
                detail="Invalid Refresh Token"
            )

        if decoded_data.get("token_expiry_time") < datetime.now(timezone.utc).timestamp():
            raise HTTPException(
                status_code=401,
                detail="Token expired"
            )
        
        return {
            "user_name":decoded_data.get("user_name"),
            "user_role":decoded_data.get("user_role")
        }

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )


######################
# FastAPI end points #
######################

@app.on_event("startup")
def create_table():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def health():
    return {"status":"Auth-endpoint is running"}

@app.post("/register")
def register(data:register_request, db:Session=Depends(get_db)):

    user_exists = db.scalar(select(User).where(User.user_name == data.user_name))

    if (user_exists):
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    new_user = User(
        user_name = data.user_name,
        password_hash = password_hash.hash(data.user_password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Error {e}"
        )
    
    return {"status":f"{data.user_name} registered successfully"}

@app.post("/login")
def login(data:login_request, db:Session=Depends(get_db)):

    user_data = db.scalar(select(User).where(User.user_name == data.user_name))

    if user_data is None or not password_hash.verify(data.user_password, user_data.password_hash):
        raise HTTPException(
            status_code=409,
            detail="User data has an error"
        )

    if user_data.id == 1:
        role = "admin"
    else: 
        role = "user"

    access = create_jwt_token(user=user_data.user_name,role=role)
    refresh = create_jwt_token(user=user_data.user_name,role=role, token_type="refresh_token")

    payload = {
        "user_name":user_data.user_name,
        "access_token": access,
        "refresh_token": refresh
    }

    return payload

@app.post("/refresh")
def refresh(data:refresh_request):
    try:
        jwt_data = jwt_decoder(data.refresh_token)
        new_access_token = create_jwt_token(user=jwt_data["user_name"],role=jwt_data["user_role"])
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"   
        )
    
    return {
        "access_token":new_access_token
    }
