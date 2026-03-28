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