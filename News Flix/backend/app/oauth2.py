# JWT expires every 30 mins
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from . import schemas, database
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings

SECRET_KEY = settings.secret_key # any string
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# used in login()
def create_access_token(user_id: dict):
    data = user_id.copy() # to avoid side effects
    #expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})   # {"user_id": 1, "exp": datetime}
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') # extracts jwt from request.

# to identify the user making the request
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # if JWT expired exception raised
        user_id = payload.get("user_id")
        if user_id is None:
            raise JWTError
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Couldnt validate credentials", headers={"WWW-Authenticate": "Bearer"}) # JWT expired or invalid
    #print(user_id)
    return user_id
