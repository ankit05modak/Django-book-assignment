import pytest

from books.models import Book


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_user(
        username="admin",
        email="a@a.com",
        password="pass",
        is_superuser=True,
        is_staff=True,
    )


@pytest.mark.django_db
def test_book_list_add_edit_delete_and_scrape(client, superuser, monkeypatch):
    # Login as superuser (has all permissions)
    client.force_login(superuser)

    # 1) Book list shows created book
    Book.objects.create(title="ListBook", genre="G", price=1)
    resp = client.get("/books/")
    assert resp.status_code == 200
    assert "ListBook" in resp.content.decode()

    # 2) Add a book via POST
    add_url = "/books/add/"
    resp = client.post(
        add_url, {"title": "Added", "genre": "X", "price": "2.50", "description": "d"}
    )
    assert resp.status_code in (302, 303)
    assert Book.objects.filter(title="Added").exists()

    # 3) Edit the book
    b = Book.objects.get(title="Added")
    edit_url = f"/books/edit/{b.pk}/"
    resp = client.post(
        edit_url,
        {"title": "Edited", "genre": "X", "price": "3.00", "description": "d2"},
    )
    assert resp.status_code in (302, 303)
    b.refresh_from_db()
    assert b.title == "Edited"

    # 4) Delete the book
    delete_url = f"/books/delete/{b.pk}/"
    resp = client.post(delete_url)
    assert resp.status_code in (302, 303)
    assert not Book.objects.filter(pk=b.pk).exists()

    # 5) Scrape endpoint triggers scraper when category provided
    called = {}

    def fake_scrape(category):
        called["category"] = category

    # The view imports `scrape_book` at module import time, so patch the name
    # on the view module to ensure the real scraper is not executed.
    monkeypatch.setattr("books.views.scrape_book", fake_scrape)
    resp = client.post("/books/scrape/", {"category": "Science"})
    assert resp.status_code in (302, 303)
    assert called.get("category") == "Science"


def test_unauthenticated_and_permission_behavior(client, django_user_model):
    # Unauthenticated users should be redirected to login for protected endpoints
    resp = client.get("/books/add/")
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")

    # Authenticated but without permissions should not get 200
    user = django_user_model.objects.create_user(username="user", password="p")
    client.force_login(user)
    resp = client.get("/books/add/")
    assert resp.status_code != 200


def test_add_invalid_data_shows_errors(client, superuser):
    client.force_login(superuser)
    resp = client.post("/books/add/", {"genre": "X", "price": "1.23"})
    # Missing required `title` should re-render form with errors
    assert resp.status_code == 200
    assert resp.context is not None
    form = resp.context.get("form")
    assert form is not None
    assert "title" in form.errors


def test_scrape_get_and_post_without_category(client, superuser):
    client.force_login(superuser)

    # GET displays categories in context
    resp = client.get("/books/scrape/")
    assert resp.status_code == 200
    assert resp.context and resp.context.get("categories")

    # POST without category should redirect back with an error message
    resp = client.post("/books/scrape/", {}, follow=True)
    assert resp.status_code == 200
    messages = list(resp.context.get("messages", []))
    assert any("Please select a category" in m.message for m in messages)


def test_edit_nonexistent_returns_404(client, superuser):
    client.force_login(superuser)
    resp = client.get("/books/edit/99999/")
    assert resp.status_code == 404


def test_delete_confirmation_and_post(client, superuser):
    client.force_login(superuser)
    b = Book.objects.create(title="ToDelete", genre="G", price=1)
    delete_url = f"/books/delete/{b.pk}/"

    # GET shows confirmation
    resp = client.get(delete_url)
    assert resp.status_code == 200
    assert "Are you sure" in resp.content.decode() or b.title in resp.content.decode()

    # POST deletes
    resp = client.post(delete_url)
    assert resp.status_code in (302, 303)
    assert not Book.objects.filter(pk=b.pk).exists()
