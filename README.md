Library Management System

A simple library management API built using Python, Flask, and SQLite. It lets you add books, register members, and keep track of books that have been borrowed and returned.

I built this project to practise and understanding the working with REST APIs, databases, and automated testing in Python as a beginner.

# What it can do

- Add books and view the list of books
- Search for books by title or author
- Prevent duplicate ISBNs
- Register library members and view registered members
- Keep track of borrowed books
- Return books and update their availability
- Handle invalid requests and duplicate entries
- Run automated tests using pytest

# Built with

- Python
- Flask
- SQLite
- pytest

# Getting started

# 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd library-management-system
```

Replace `YOUR_REPOSITORY_URL` with the URL of this repository.

# 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

# 3. Install the required packages

```bash
pip install -r requirements.txt
```

# 4. Run the application

```bash
python3 app.py
```

The API will be available at `http://127.0.0.1:5000`.

The SQLite database is created locally when the application starts.

# API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | Check if the API is running |
| GET | `/books` | Get all books |
| POST | `/books` | Add a book |
| GET | `/books/search?q=Python` | Search by title or author |
| POST | `/members` | Register a member |
| GET | `/members` | Get all members |
| POST | `/loans` | Borrow a book |
| GET | `/loans` | View loan records |
| PUT | `/loans/<loan_id>/return` | Return a book |

# Example requests

# Add a book

```bash
curl -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Python Basics","author":"Alex Smith","isbn":"9780000000001","quantity":2}'
```

# Register a member

```bash
curl -X POST http://127.0.0.1:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name":"Jamie Lee","email":"jamie@example.com"}'
```

# Borrow a book

Use the book and member IDs returned by the API.

```bash
curl -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"member_id":1}'
```

# Return a book

Replace `1` with the loan ID returned when the book was borrowed.

```bash
curl -X PUT http://127.0.0.1:5000/loans/1/return
```

# Running the tests

Run the tests from the project folder:

```bash
python3 -m pytest -v
```

The tests cover book creation, search, duplicate entries, member registration, borrowing, and returning books.

# Project structure

```text
library-management-system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_app.py
```

# Things I want to add next

- Update and delete books
- Better email validation
- Due dates and overdue tracking
- Login and access control
- API documentation

