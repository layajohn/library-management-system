
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = "library.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            quantity INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            borrowed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            returned_at TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return jsonify({
        "message": "Library Management System API is running!"
    })


@app.route("/members", methods=["POST"])
def add_member():
    data = request.get_json(silent=True)

    # Check that the request contains a JSON object
    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object"}), 400

    name = data.get("name")
    email = data.get("email")

    # Validate the member's name
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    # Validate the member's email
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Email is required"}), 400

    name = name.strip()
    email = email.strip().lower()

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "INSERT INTO members (name, email) VALUES (?, ?)",
            (name, email)
        )

        connection.commit()

        member = connection.execute(
            "SELECT * FROM members WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(dict(member)), 201

    except sqlite3.IntegrityError:
        connection.rollback()
        return jsonify({
            "error": "This email is already registered"
        }), 409

    finally:
        connection.close()

@app.route("/members", methods=["GET"])
def get_members():
    connection = get_db_connection()

    members = connection.execute(
        "SELECT * FROM members ORDER BY id"
    ).fetchall()

    connection.close()

    return jsonify([dict(member) for member in members])


@app.route("/loans", methods=["POST"])
def borrow_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object"}), 400

    book_id = data.get("book_id")
    member_id = data.get("member_id")

    if type(book_id) is not int or book_id < 1:
        return jsonify({"error": "Valid book_id is required"}), 400

    if type(member_id) is not int or member_id < 1:
        return jsonify({"error": "Valid member_id is required"}), 400

    connection = get_db_connection()

    try:
        # Begin a write transaction before checking availability
        connection.execute("BEGIN IMMEDIATE")

        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        if book is None:
            connection.rollback()
            return jsonify({"error": "Book not found"}), 404

        member = connection.execute(
            "SELECT * FROM members WHERE id = ?",
            (member_id,)
        ).fetchone()

        if member is None:
            connection.rollback()
            return jsonify({"error": "Member not found"}), 404

        # Update availability only if a copy remains
        update = connection.execute(
            """
            UPDATE books
            SET available = available - 1
            WHERE id = ? AND available > 0
            """,
            (book_id,)
        )

        if update.rowcount != 1:
            connection.rollback()
            return jsonify({
                "error": "No copies of this book are available"
            }), 409

        cursor = connection.execute(
            """
            INSERT INTO loans (book_id, member_id)
            VALUES (?, ?)
            """,
            (book_id, member_id)
        )

        connection.commit()

        loan = connection.execute(
            "SELECT * FROM loans WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(dict(loan)), 201

    except sqlite3.Error:
        connection.rollback()
        app.logger.exception("Failed to borrow book")
        return jsonify({
            "error": "A database error occurred while borrowing the book"
        }), 500

    finally:
        connection.close()


@app.route("/loans/<int:loan_id>/return", methods=["PUT"])
def return_book(loan_id):
    connection = get_db_connection()

    try:
        # Start a write transaction
        connection.execute("BEGIN IMMEDIATE")

        loan = connection.execute(
            "SELECT * FROM loans WHERE id = ?",
            (loan_id,)
        ).fetchone()

        if loan is None:
            connection.rollback()
            return jsonify({"error": "Loan not found"}), 404

        if loan["returned_at"] is not None:
            connection.rollback()
            return jsonify({
                "error": "This book has already been returned"
            }), 409

        # Mark the loan as returned only if it is still active
        update_loan = connection.execute(
            """
            UPDATE loans
            SET returned_at = CURRENT_TIMESTAMP
            WHERE id = ? AND returned_at IS NULL
            """,
            (loan_id,)
        )

        if update_loan.rowcount != 1:
            connection.rollback()
            return jsonify({
                "error": "This book has already been returned"
            }), 409

        # Restore one available copy
        update_book = connection.execute(
            """
            UPDATE books
            SET available = available + 1
            WHERE id = ? AND available < quantity
            """,
            (loan["book_id"],)
        )

        if update_book.rowcount != 1:
            connection.rollback()
            return jsonify({
                "error": "Could not update book availability"
            }), 409

        connection.commit()

        updated_loan = connection.execute(
            "SELECT * FROM loans WHERE id = ?",
            (loan_id,)
        ).fetchone()

        return jsonify(dict(updated_loan)), 200

    except sqlite3.Error:
        connection.rollback()
        app.logger.exception("Failed to return book")
        return jsonify({
            "error": "A database error occurred while returning the book"
        }), 500

    finally:
        connection.close()

@app.route("/loans", methods=["GET"])
def get_loans():
    connection = get_db_connection()

    loans = connection.execute(
        """
        SELECT
            loans.id,
            loans.book_id,
            books.title AS book_title,
            loans.member_id,
            members.name AS member_name,
            loans.borrowed_at,
            loans.returned_at
        FROM loans
        JOIN books ON loans.book_id = books.id
        JOIN members ON loans.member_id = members.id
        ORDER BY loans.id
        """
    ).fetchall()

    connection.close()

    return jsonify([dict(loan) for loan in loans])

@app.route("/books/search", methods=["GET"])
def search_books():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Please provide a search term using ?q="
        }), 400

    connection = get_db_connection()

    books = connection.execute(
        """
        SELECT * FROM books
        WHERE title LIKE ? OR author LIKE ?
        ORDER BY id
        """,
        (f"%{query}%", f"%{query}%")
    ).fetchall()

    connection.close()

    return jsonify([dict(book) for book in books])

@app.route("/books", methods=["GET"])
def get_books():
    connection = get_db_connection()

    books = connection.execute(
        "SELECT * FROM books ORDER BY id"
    ).fetchall()

    connection.close()

    return jsonify([dict(book) for book in books])


@app.route("/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a valid JSON object"}), 400

    title = data.get("title")
    author = data.get("author")
    isbn = data.get("isbn")
    quantity = data.get("quantity", 1)

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(author, str) or not author.strip():
        return jsonify({"error": "Author is required"}), 400

    if isbn is not None and (
        not isinstance(isbn, str) or not isbn.strip()
    ):
        return jsonify({"error": "ISBN must be valid text"}), 400

    if type(quantity) is not int or quantity < 1:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO books (title, author, isbn, quantity, available)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                author.strip(),
                isbn.strip() if isbn else None,
                quantity,
                quantity
            )
        )

        connection.commit()

        book = connection.execute(
            "SELECT * FROM books WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(dict(book)), 201

    except sqlite3.IntegrityError:
        connection.rollback()
        return jsonify({"error": "This ISBN already exists"}), 409

    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
