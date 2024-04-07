from django.contrib.auth.models import User
import graphene
from .types import UserType

class UserQuery(graphene.ObjectType):
    all_users = graphene.List(
        UserType, 
        description="Retrieve all users."
    )
    user_by_id = graphene.Field(
        UserType,
        id=graphene.Int(required=True, description="The ID of the user to retrieve."),
        description="Retrieve a single user by its ID."
    )
    search_users = graphene.List(
        UserType,
        username=graphene.String(default_value=None, description="A substring of the user name to filter by. Case-insensitive."),
        email=graphene.String(default_value=None, description="A substring of the user email to filter by. Case-insensitive."),
        description="Search for users based on various criteria such as name and email."
    )

    def resolve_all_users(self, info):
        """
        Fetches all users from the database.
        
        Returns:
            List of all users.
        """
        return User.objects.all()
    
    def resolve_user_by_id(self, info, id):
        """
        Retrieves a single user by its ID.

        Returns:
            A user if found, None otherwise.
        """
        return User.objects.filter(pk=id).first()
    
    def resolve_search_users(self, info, username, email):
        """
        Search for users based on various criteria such as name and email.

        Returns:
            List of users that match the search criteria.
        """
        queryset = User.objects.all()
        if username:
            queryset = queryset.filter(username__icontains=username)
        if email:
            queryset = queryset.filter(email__icontains=email)
        return queryset