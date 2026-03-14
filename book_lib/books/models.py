from django.db import models


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
