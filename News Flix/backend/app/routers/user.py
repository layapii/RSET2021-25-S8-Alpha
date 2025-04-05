from fastapi import HTTPException, Response, status, Depends, APIRouter
from .. import schemas, utils, oauth2
from ..database import conn, cursor
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
#from .. import database as db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    try:
        cursor.execute("""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *""", (user.email, user.password))
        new_user = cursor.fetchone()
        conn.commit()
        return new_user
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="ToDo server error")
   

# POST can handle request body securely
@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):

    #OAuth2PasswordRequestForm only has username and password
    cursor.execute("""SELECT * FROM users WHERE email = %s""", (user_credentials.username,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Username")
    
    if not utils.verify(user_credentials.password, user['password']):  # True if password is correct
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    #return  token
    access_token = oauth2.create_access_token(user_id={"user_id": user['id']})
    return {"access_token": access_token, "token_type": "bearer"} # token_type is needed for OAuth2 compliance
