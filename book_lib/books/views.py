# Create your views here.
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import BookForm
from .models import Book
from .constants import BOOK_CATEGORIES


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def get_queryset(self):
        queryset = Book.objects.all()

        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(genre__icontains=search)
            )

        return queryset


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("book-list")
    permission_required = "books.add_book"


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    success_url = reverse_lazy("book-list")
    permission_required = "books.change_book"


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book-list")
    permission_required = "books.delete_book"


class ScrapeBooksView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "books.add_book"
    template_name = "books/scrape_books.html"

    def get(self, request):
        # Show dropdown
        return render(request, self.template_name, {"categories": BOOK_CATEGORIES})

    def post(self, request):
        # Handle scrape trigger
        category = request.POST.get("category")
        if not category:
            messages.error(request, "Please select a category")
            return redirect("scrape-books")

        # For now just show a success message
        messages.success(request, f"Scraping triggered for category: {category}")
        return redirect("scrape-books")
