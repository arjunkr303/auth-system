from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import get_connection
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import random
import requests
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class SendOTP(BaseModel):
    phone_number: str

class VerifyOTP(BaseModel):
    phone_number: str
    otp_code: str



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

    if not existing_user["is_verified"]:
        return {"error": "Phone number not verified! Please verify your OTP first. ❌"}

    token = create_token({"phone": existing_user["phone_number"]})

    return {
        "message": "Login successful! ✅",
        "token": token,
        "user": {
            "id": existing_user["id"],
            "customer_name": existing_user["customer_name"],
            "phone_number": existing_user["phone_number"],
            "is_verified": existing_user["is_verified"]
        }
    }


@app.post("/send-otp")
def send_otp(data: SendOTP):
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=5)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO otps (phone_number, otp_code, expires_at) VALUES (%s, %s, %s)",
        (data.phone_number, otp_code, expires_at)
    )
    conn.commit()
    cursor.close()
    conn.close()

    headers = {
        "Authorization": f"Bearer {os.getenv('SYNXZAP_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://api.synxzap.com/api/v1/messages/send-otp",
        json={"phoneNumber": data.phone_number, "otp": otp_code},
        headers=headers
    )

    if response.status_code == 200:
        return {"message": "OTP sent successfully! ✅"}
    else:
        return {"error": "Failed to send OTP ❌", "details": response.json()}


@app.post("/verify-otp")
def verify_otp(data: VerifyOTP):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM otps
        WHERE phone_number = %s
        AND otp_code = %s
        AND is_used = FALSE
        AND expires_at > NOW()
        ORDER BY created_at DESC
        LIMIT 1
    """, (data.phone_number, data.otp_code))

    otp_record = cursor.fetchone()

    if not otp_record:
        cursor.close()
        conn.close()
        return {"error": "Invalid or expired OTP! ❌"}

    cursor.execute("UPDATE otps SET is_used = TRUE WHERE id = %s", (otp_record["id"],))
    cursor.execute("UPDATE users SET is_verified = TRUE WHERE phone_number = %s", (data.phone_number,))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Phone number verified successfully! ✅"}


@app.get("/me")
def get_me(phone: str = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, customer_name, phone_number, is_verified, created_at FROM users WHERE phone_number = %s", (phone,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/logout")
def logout(phone: str = Depends(get_current_user)):
    return {"message": "Logged out successfully! ✅"}