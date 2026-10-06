# Library Database Management System

A simple, beginner-friendly Library Database Management System built for a college DBMS project. It uses HTML, CSS, Vanilla JavaScript for the frontend, Python's standard library HTTP server for the backend, and MySQL as the database.

## Features

- **Dashboard**: View total books, available copies, total members, currently issued books, and overdue books
- **Books Management**: Add, edit, delete, search, and view books
- **Members Management**: Add, edit, delete, search, and view members
- **Loan Management**: Issue books, return books, view all loan records, and view overdue loans
- **Transactions**: Uses database transactions for issue/return operations
- **Validation**: Proper checks for book availability, duplicate returns, and delete restrictions

## Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python 3 (standard library `http.server`)
- **Database**: MySQL
- **Connectivity**: `mysql-connector-python`

## Architecture

```
HTML/CSS/JavaScript
        ↓ HTTP/JSON
Python Backend (http.server)
        ↓ mysql-connector-python
MySQL Database (library_management)
```

The browser never connects directly to MySQL - all database operations go through the Python backend.

## Database Schema

### books
- `book_id` (PK, AUTO_INCREMENT)
- `title`, `author`, `isbn` (UNIQUE), `category`
- `total_copies`, `available_copies`

### members
- `member_id` (PK, AUTO_INCREMENT)
- `name`, `email`, `phone`, `join_date`

### loans
- `loan_id` (PK, AUTO_INCREMENT)
- `book_id` (FK → books.book_id)
- `member_id` (FK → members.member_id)
- `issue_date`, `due_date`, `return_date` (NULL if not returned)

## Prerequisites

- Python 3.6+
- MySQL Server (installed and running)
- pip (Python package manager)

## Setup Instructions

### 1. Clone/Download the Project
Navigate to the project directory:
```bash
cd library-management-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database

Create and populate the database using the SQL files:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/sample_data.sql
```

### 4. Configure Database Credentials

Create a `.env` file in the project root (or set environment variables):

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=library_management
DB_PORT=3306
```

You can also set environment variables directly without creating a `.env` file.

### 5. Run the Application

Start the Python server:
```bash
cd backend
python server.py
```

The server will start at `http://localhost:8000`

### 6. Access the Application

Open your web browser and go to:
```
http://localhost:8000
```

## Usage Guide

1. **Dashboard**: Get an overview of the library's current status
2. **Books**: Click "Books" → "Add Book" to add new books. Use the search bar to find books by title, author, ISBN, or category
3. **Members**: Add library members with their details
4. **Issue Book**: Go to "Issue Book" → Enter Book ID and Member ID → Set dates → Issue
5. **Return Book**: Go to "Return Book" → Enter Loan ID → Return
6. **Loan Records**: View all loans or filter by overdue loans

## Sample Data

The sample data includes:
- 5 books (including one with 0 available copies to demonstrate availability checks)
- 4 members
- 4 loan records (some returned, some active, some overdue)

## Important Notes

- The application does not use authentication - it's designed for a college DBMS demo
- All database operations use parameterized queries to prevent SQL injection
- Issue/Return operations use transactions to ensure data consistency
- Books/members with active loans cannot be deleted
- Available copies are automatically updated on issue/return

## Project Structure

```
library-management-system/
├── backend/
│   ├── server.py      # Main HTTP server & API endpoints
│   ├── database.py    # Database connection helper
│   ├── books.py       # Books CRUD operations
│   ├── members.py     # Members CRUD operations
│   └── loans.py       # Loan operations (issue/return)
├── frontend/
│   ├── index.html     # Main UI
│   ├── css/style.css  # Styling
│   └── js/app.js      # Frontend logic
├── database/
│   ├── schema.sql     # Database schema
│   └── sample_data.sql # Sample test data
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
├── requirements.txt   # Python dependencies
└── README.md          # Documentation
```

## License

This project is for educational purposes.
