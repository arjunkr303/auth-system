# Synx AI & Automation — Auth System

A production-ready authentication system built with **FastAPI**, **MySQL**, and **Synxzap WhatsApp API**. It features secure user registration, WhatsApp OTP verification, JWT-based authentication, and a modern, responsive frontend.

## Features

- **User Registration**: Register users securely with their phone number and full name.
- **WhatsApp OTP Verification**: Verify users via OTP sent to their WhatsApp using the Synxzap API.
- **Secure Authentication**: Login system with phone number and password utilizing JWT (JSON Web Tokens) for session management.
- **Password Security**: Passwords are securely hashed using `bcrypt`.
- **Modern UI**: Includes a responsive, animated, and minimalist dark-mode frontend (`index.html` and `dashboard.html`).
- **RESTful API**: Clean API endpoints powered by FastAPI.

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: MySQL (`mysql-connector-python`)
- **Authentication**: JWT (`python-jose`), `bcrypt`
- **External API**: Synxzap API (for WhatsApp Messages)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Setup Instructions

### 1. Requirements
- **Python 3.8+**
- **MySQL Server**
- **Synxzap API Key** (for sending OTPs via WhatsApp)

### 2. Clone the repository
```bash
git clone <your-github-repo-url>
cd auth-system
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Database Setup
Create a MySQL database and the required tables.

```sql
CREATE DATABASE auth_system;

USE auth_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE otps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Environment Variables
Create a `.env` file in the root directory and add the following context (update the values with your actual credentials):

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=auth_system
PORT=8000
SYNXZAP_API_TOKEN=your_synxzap_api_key
SECRET_KEY=your_secure_random_secret_key
```

*Note: You can generate a strong `SECRET_KEY` using `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`.*

### 6. Run the Application
Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- The backend API will be available at: `http://localhost:8000`
- Interactive API Documentation (Swagger UI): `http://localhost:8000/docs`

### 7. Run the Frontend
Simply open `index.html` in your web browser. Ensure the FastAPI backend is running so the frontend can successfully communicate with the API.

## API Endpoints

- `GET /` - Health check.
- `POST /register` - Register a new user.
- `POST /login` - Login and get a JWT token.
- `POST /send-otp` - Send verification OTP to WhatsApp.
- `POST /verify-otp` - Verify the OTP to activate the account.
- `GET /me` - Get current logged-in user details (requires JWT).
- `POST /logout` - Logout the user.

## License
MIT License
