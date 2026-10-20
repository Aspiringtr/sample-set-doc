import os
from dotenv import load_dotenv
from typing import Annotated
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.orm import Session

from data_base.database import get_db, engine, Base
from crud.model import Item
from auth.model import User

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JWT_KEY = os.environ.get("JWT_KEY")
JWT_ALGO = os.environ.get("JWT_ALGO")

app = FastAPI(title="crud-survices")

bearer = HTTPBearer()


class Insert_item(BaseModel):
    item_name:str =Field(min_length=1,max_length=100)
    item_description:str =Field(default="",max_length=200)

class Update_item(BaseModel):
    item_id:int
    item_name:str
    item_description:str

def validate_token(
        token:Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
        db:Annotated[Session,Depends(get_db)]
        ) -> dict:
    
    try:
        decoded_token = jwt.decode(jwt=token.credentials,key=JWT_KEY,algorithms=JWT_ALGO)
        user_identification_number = db.scalar(select(User).where(User.user_name == decoded_token.get('user_name')))

        if decoded_token.get("token_type") != "access_token":
            raise HTTPException(
                status_code=401,
                detail="Invalid Access token"
            )

        if decoded_token.get("token_expiry_time") < datetime.now(timezone.utc).timestamp():
            raise HTTPException(
                status_code=401,
                detail="Expired token"
            )

        return {
            "user_name":decoded_token.get("user_name"),
            "user_role":decoded_token.get("user_role"),
            "user_id":user_identification_number.id
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=401,
            detail="Something went wrong at Token validation"
        )
    
@app.on_event("startup")
def database_creation():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def health():
    return{"status":"Healthy and running at port 8002"}

@app.get("/item")
def get_all_item(
        db:Annotated[Session,Depends(get_db)],
        user_data:Annotated[dict,Depends(validate_token)]
    ):

    try:
        all_items = db.scalars(select(Item).where(Item.user_id == user_data.get('user_id'))).all()

        if not all_items:
            raise HTTPException(
                status_code=404,
                detail="Item not found or does not exist"
            )

        return all_items

    except Exception as e:
        print(f"ERROR:{e}")
        raise HTTPException(
            status_code=500,
            detail=f"ERROR: {e}"
        )

@app.get("/item/{item_id}")
def get_one_item(
        item_id:int,
        db:Annotated[Session,Depends(get_db)],
        user_data:Annotated[dict,Depends(validate_token)]
    ):

    try:
        get_item = db.scalar(select(Item).where(Item.id == item_id))

        if not get_item or get_item.user_id != user_data.get('user_id'):
            raise HTTPException(
                status_code=404,
                detail="Item not found or does not exist"
            )
        
        return get_item

    except Exception as e:
        print(f"ERROR:{e}")
        raise HTTPException(
            status_code=500,
            detail=f"ERROR: {e}"
        )

@app.post("/item")
def insert_item(
        data:Insert_item,
        db:Annotated[Session,Depends(get_db)],
        user_data:Annotated[dict,Depends(validate_token)]
    ):

    insert_data = Item(
        item_name = data.item_name,
        item_description = data.item_description,
        user_id = user_data.get('user_id')
    )
    

    try:
        db.add(insert_data)
        db.commit()
        db.refresh(insert_data)
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error occured during data uploading"
        )

    return {
        "status":"ok",
        "content":"Inserted the data"
    }

@app.put("/item")
def update_item(
        data:Update_item,
        db:Annotated[Session,Depends(get_db)],
        user_data:Annotated[dict,Depends(validate_token)]
    ):
    try:
        item_update = db.scalar(select(Item).where(Item.id == data.item_id))

        if item_update.user_id != user_data.get('user_id'):
            raise HTTPException(
                status_code=404,
                detail=f"Item not found"
            )            

        item_update.item_name = data.item_name
        item_update.item_description = data.item_description

        db.commit()
        db.refresh(item_update)
        return{
            "status":"ok",
            "content":"Successfully updated the data"
        }

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ERROR: {e}"
        )

@app.delete("/item/{item_id}")
def delete_item(
        item_id:int,
        db:Annotated[Session,Depends(get_db)],
        user_data:Annotated[dict,Depends(validate_token)]
    ):

    try:
        delete_item = db.scalar(select(Item).where(Item.id == item_id))
        
        if delete_item.user_id == user_data.get('user_id') or user_data.get('user_role') == "admin":

            if not delete_item:
                raise HTTPException(
                    status_code=404,
                    detail="Item not found or does not exist"
                )

            db.delete(delete_item)
            db.commit()

            return{
                "status":"ok",
                "content":"deleted the data"            
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="You have no access"
            )

    except Exception as e:
        db.rollback()
        print(f"ERROR:{e}")
        raise HTTPException(
            status_code=500,
            detail=f"ERROR: {e}"
        )