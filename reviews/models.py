from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Review(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return self.title
