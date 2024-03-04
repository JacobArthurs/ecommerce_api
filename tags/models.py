from django.db import models
from products.models import Product

class Tag(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ManyToManyField(Product, related_name='tags')

    def __str__(self):
        return self.name
