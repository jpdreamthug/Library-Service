# Library-Service
Group project of students of the mate-academy
## Overview
API service for library management written on DRF
This project is a library management system designed to handle
book inventory, user management, borrowing transactions,
notifications, and payments. It integrates with Stripe for 
payment processing and Telegram for notifications.

## Participants:
- Yaroslav Kondrattsev
- Dmytro Sokolovskyi
- Ivan Vahanov
- Danylo Roh
- Andrii Fedorov
- Serhii Musiienko

## Installing using GitHub
Install PostgresSQL and create db
```
git clone https://github.com/jpdreamthug/Library-Service.git
cd Library-Service
python - m venv venv
sourse venv/bin/activate
pip install - r requiments.txt
create correct .env file from .env.sample
python manage.py migrate
python manage.py runserver
```

## Run with docker
Docker should be installed.
You should create correct .env file from .env.sample
```
docker-compose build
docker-compose up
```
or
```
docker-compose up --build
```
Access the application: Open your browser and go to http://localhost:8001

### Authentication

To use the API, you need to create a user account and obtain an access token:

1. Create a user:
POST /user/register/
2. Get an access token:
POST /user/token/
Include the access token in the Authorization header for authenticated requests:
Authorization: Bearer <your_access_token>

## Features
- **JWT authentification**
- **Admin panel /admin/**
- **Documentation is located at /api/doc/swagger/**
- **Books Service**: Manage book inventory with CRUD operations.
- **Users Service**: Handle user authentication and registration.
- **Borrowings Service**: Manage book borrowings, including creation, retrieval, and return.
- **Notifications Service**: Send notifications about borrowings and overdue items via Telegram.
- **Payments Service**: Handle payments for book borrowings through Stripe.
### Components and API Endpoints
For detailed API documentation, visit /api/schema/swagger-ui/ when the server is running.
### Books Service
- **API Endpoints**:
  - `POST /api/books/` - Add a new book
  - `GET /api/books/` - List all books
  - `GET /api/books/<id>/` - Get details of a specific book
  - `PUT/PATCH /api/books/<id>/` - Update a book (including inventory management)
  - `DELETE /api/books/<id>/` - Delete a book

### Users Service
- **API Endpoints**:
  - `POST /users/` - Register a new user
  - `POST /users/token/` - Get JWT tokens
  - `POST /users/token/refresh/` - Refresh JWT token
  - `GET /users/me/` - Get profile information of the current user
  - `PUT/PATCH /users/me/` - Update profile information

### Borrowings Service
- **API Endpoints**:
  - `POST /api/borrowings/` - Create a new borrowing (decreases book inventory by 1)
  - `GET /api/borrowings/?user_id=...&is_active=...` - List borrowings by user ID and active status
  - `GET /api/borrowings/<id>/` - Get details of a specific borrowing
  - `POST /api/borrowings/<id>/return/` - Set actual return date (increases book inventory by 1)

### Notifications Service (Telegram)
- **Functionality**:
  - Notifications about new borrowings, overdue items, and successful payments.
  - Uses Telegram API, Telegram Chats & Bots.
  - Implemented as a parallel cluster/process (Django Q or Django Celery).

### Payments Service (Stripe)
- **API Endpoints**:
  - `GET /success/` - Check for successful Stripe payment
  - `GET /cancel/` - Handle payment cancellation

## Architecture diagram

Here is the architecture diagram for the project:

![architecture diagram](assets/shema.png)