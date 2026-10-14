
import pytest
import app as library_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate database for testing
    test_database = tmp_path / "test_library.db"

    monkeypatch.setattr(
        library_app, "DATABASE", str(test_database)
    )

    library_app.init_db()

    library_app.app.config["TESTING"] = True

    with library_app.app.test_client() as client:
        yield client


def create_book(client, isbn="9780000000001", quantity=2):
    return client.post(
        "/books",
        json={
            "title": "Python Basics",
            "author": "Alex Smith",
            "isbn": isbn,
            "quantity": quantity
        }
    )


def create_member(client):
    return client.post(
        "/members",
        json={
            "name": "Jamie Lee",
            "email": "jamie@example.com"
        }
    )


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == (
        "Library Management System API is running!"
    )


def test_add_book(client):
    response = create_book(client)

    assert response.status_code == 201
    assert response.json["title"] == "Python Basics"
    assert response.json["quantity"] == 2
    assert response.json["available"] == 2


def test_duplicate_isbn_rejected(client):
    create_book(client)

    response = create_book(client)

    assert response.status_code == 409


def test_search_books(client):
    create_book(client)

    response = client.get("/books/search?q=Python")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "Python Basics"


def test_search_without_query_rejected(client):
    response = client.get("/books/search")

    assert response.status_code == 400


def test_register_member(client):
    response = create_member(client)

    assert response.status_code == 201
    assert response.json["name"] == "Jamie Lee"


def test_duplicate_email_rejected(client):
    create_member(client)

    response = create_member(client)

    assert response.status_code == 409


def test_borrow_book_decreases_availability(client):
    book = create_book(client)
    member = create_member(client)

    response = client.post(
        "/loans",
        json={
            "book_id": book.json["id"],
            "member_id": member.json["id"]
        }
    )

    assert response.status_code == 201

    books = client.get("/books").json
    assert books[0]["available"] == 1


def test_return_book_restores_availability(client):
    book = create_book(client)
    member = create_member(client)

    loan = client.post(
        "/loans",
        json={
            "book_id": book.json["id"],
            "member_id": member.json["id"]
        }
    )

    loan_id = loan.json["id"]

    response = client.put(f"/loans/{loan_id}/return")

    assert response.status_code == 200
    assert response.json["returned_at"] is not None

    books = client.get("/books").json
    assert books[0]["available"] == 2


def test_cannot_return_loan_twice(client):
    book = create_book(client)
    member = create_member(client)

    loan = client.post(
        "/loans",
        json={
            "book_id": book.json["id"],
            "member_id": member.json["id"]
        }
    )

    loan_id = loan.json["id"]

    client.put(f"/loans/{loan_id}/return")
    response = client.put(f"/loans/{loan_id}/return")

    assert response.status_code == 409

def test_borrow_nonexistent_book(client):
    member = create_member(client)

    response = client.post(
        "/loans",
        json={
            "book_id": 999,
            "member_id": member.json["id"]
        }
    )

    assert response.status_code == 404
    assert response.json["error"] == "Book not found"


def test_cannot_borrow_more_than_available(client):
    book = create_book(client, quantity=1)
    member = create_member(client)

    first_loan = client.post(
        "/loans",
        json={
            "book_id": book.json["id"],
            "member_id": member.json["id"]
        }
    )

    assert first_loan.status_code == 201

    second_loan = client.post(
        "/loans",
        json={
            "book_id": book.json["id"],
            "member_id": member.json["id"]
        }
    )

    assert second_loan.status_code == 409
    assert second_loan.json["error"] == (
        "No copies of this book are available"
    )
