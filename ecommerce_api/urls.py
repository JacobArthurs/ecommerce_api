from django.contrib import admin
from django.conf import settings
from django.urls import path
from graphene_django.views import GraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql', GraphQLView.as_view(graphiql=settings.DEBUG)),
]
