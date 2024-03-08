import graphene
from graphene_django import DjangoObjectType
from .models import Tag

class TagType(DjangoObjectType):
    """
    Represents the tag model in GraphQL. This type exposes all fields of the tag model,
    facilitating queries on tags in the database.
    """
    class Meta:
        model = Tag
        fields = '__all__'