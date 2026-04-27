from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import get_connection
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Synx AI Auth API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain.encode('utf-8')[:72]
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

# ─── Models ───────────────────────────────────────────────────
class User(BaseModel):
    customer_name: str
    phone_number: str
    password: str

class LoginUser(BaseModel):
    phone_number: str
    password: str


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone = payload.get("phone")
        if phone is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return phone
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ─── Routes ───────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Auth system is running! ✅"}


@app.post("/register")
def register(user: User):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE phone_number = %s",
        (user.phone_number,)
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return {"error": "Account already exists! ❌"}

    hashed = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (customer_name, phone_number, password) VALUES (%s, %s, %s)",
        (user.customer_name, user.phone_number, hashed)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User registered successfully! ✅"}


@app.post("/login")
def login(user: LoginUser):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE phone_number = %s",
        (user.phone_number,)
    )
    existing_user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not existing_user:
        return {"error": "Phone number not found! ❌"}

    if not verify_password(user.password, existing_user["password"]):
        return {"error": "Wrong password! ❌"}



    token = create_token({"phone": existing_user["phone_number"]})

    return {
        "message": "Login successful! ✅",
        "token": token,
        "user": {
            "id": existing_user["id"],
            "customer_name": existing_user["customer_name"],
            "phone_number": existing_user["phone_number"]
        }
    }





@app.get("/me")
def get_me(phone: str = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, customer_name, phone_number, created_at FROM users WHERE phone_number = %s", (phone,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/logout")
def logout(phone: str = Depends(get_current_user)):
    return {"message": "Logged out successfully! ✅"}