from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
import graphene

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

    groups = graphene.List(graphene.String)

    def resolve_groups(self, info):
        return [group.name for group in self.groups.all()]