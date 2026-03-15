from django.db import models


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255, unique=True)
    genre = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
