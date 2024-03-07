import graphene
from graphene_django import DjangoObjectType
from .models import Review

class ReviewType(DjangoObjectType):
    """
    Represents the Review model in GraphQL. This type exposes all fields of the Review model,
    facilitating queries on reviews in the database.
    """
    class Meta:
        model = Review
        fields = '__all__'