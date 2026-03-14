from django.urls import path
from .views import (
    BookListView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
    ScrapeBooksView,
)

urlpatterns = [
    path("", BookListView.as_view(), name="book-list"),
    path("add/", BookCreateView.as_view(), name="book-add"),
    path("edit/<int:pk>/", BookUpdateView.as_view(), name="book-edit"),
    path("delete/<int:pk>/", BookDeleteView.as_view(), name="book-delete"),
    path("scrape/", ScrapeBooksView.as_view(), name="scrape-books"),
]
