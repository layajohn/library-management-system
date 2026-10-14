# Library Management System API

A RESTful library management API built using Python, Flask, and SQLite. It allows users to manage books, register library members, and track borrowed and returned books.

I built this project to practise working with REST APIs, databases, and automated testing in Python while developing my backend programming skills.

## Features

- Add books and retrieve the list of books
- Search for books by title or author
- Prevent duplicate ISBN entries
- Register library members and retrieve member records
- Borrow books and track loan records
- Return borrowed books and update book availability
- Handle invalid requests and duplicate entries
- Run automated tests using pytest

## Tech Stack

- **Language:** Python
- **Backend framework:** Flask
- **Database:** SQLite
- **Testing:** pytest
- **Version control:** Git and GitHub

## Getting Started

### Prerequisites

- Python 3
- Git

### 1. Clone the repository

```bash
git clone https://github.com/layajohn/library-management-system.git
cd library-management-system
```

### 2. Create and activate a virtual environment

On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python3 app.py
```

The API will be available at:

`http://127.0.0.1:5000`

The SQLite database is created locally when the application starts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check API status |
| GET | `/books` | Retrieve all books |
| POST | `/books` | Add a book |
| GET | `/books/search?q=Python` | Search books by title or author |
| POST | `/members` | Register a member |
| GET | `/members` | Retrieve registered members |
| POST | `/loans` | Borrow a book |
| GET | `/loans` | Retrieve loan records |
| PUT | `/loans/<loan_id>/return` | Return a borrowed book |

## Example Requests

The following examples use `curl`. Start the application before running them.

### Add a book

```bash
curl -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Python Basics","author":"Alex Smith","isbn":"9780000000001","quantity":2}'
```

### Register a member

```bash
curl -X POST http://127.0.0.1:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name":"Jamie Lee","email":"jamie@example.com"}'
```

### Borrow a book

Use valid book and member IDs returned by the API.

```bash
curl -X POST http://127.0.0.1:5000/loans \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"member_id":1}'
```

### Return a book

Replace `1` with the actual loan ID.

```bash
curl -X PUT http://127.0.0.1:5000/loans/1/return
```

## Running the Tests

Run the automated test suite from the project directory:

```bash
python -m pytest -v
```

The current test suite contains 12 tests covering book creation, searching, duplicate entries, member registration, borrowing, returning, and availability checks.

**Latest test result:** 12 passed.

## Project Structure

```text
library-management-system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_app.py
```

## Planned Improvements

- Update and delete book records
- Improve email validation
- Add loan due dates and overdue tracking
- Introduce authentication and access control
- Add interactive API documentation

## Learning Outcomes

Through this project, I practised building REST API endpoints with Flask, working with a SQLite database, validating requests, managing book loans, writing automated tests, and using Git and GitHub for version control.