from passlib.context import CryptContext
import logging
logging.getLogger('passlib').setLevel(logging.ERROR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # settings for password hashing

# used in create_user()
def hash(password: str):
    return pwd_context.hash(password)   # returns hashed password

# used in login()
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) # returns True or False