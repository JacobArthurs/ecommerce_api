import graphene
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from gql.types import OperationResult
from graphql_jwt.decorators import user_passes_test

class RegisterUser(graphene.Mutation):
    """
    Registers a new user with the specified username, password, and email.
    """
    class Arguments:
        username = graphene.String(required=True, description="The username of the new user.")
        password = graphene.String(required=True, description="The password of the new user.")
        email = graphene.String(required=True, description="The email of the new user.")

    operation_result = graphene.Field(OperationResult)

    @staticmethod
    def mutate(oot, info, username, password, email):
        try:
            validate_email(email)
            
            if User.objects.filter(username=username).exists():
                return RegisterUser(operation_result=OperationResult(success=False, message="Username already exists."))
            if User.objects.filter(email=email).exists():
                return RegisterUser(operation_result=OperationResult(success=False, message="Email already registered."))

            user = User.objects.create_user(username=username, email=email, password=password)
            group = Group.objects.get(name='user')
            user.groups.add(group)
            user.save()

            return RegisterUser(operation_result=OperationResult(success=True, message="User registered successfully."))
        except ValidationError as e:
            return RegisterUser(operation_result=OperationResult(success=False, message=str(e)))
        except Exception as e:
            return RegisterUser(operation_result=OperationResult(success=False, message="An unexpected error occurred."))
        
class MakeAdmin(graphene.Mutation):
    """
    Makes the specified user an admin.
    """
    class Arguments:
        user_id = graphene.Int(required=True)

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_staff = True
            user.is_superuser = True
            user.groups.clear()
            user.groups.add(Group.objects.get(name='admin'))
            user.save()
            return MakeAdmin(operation_result=OperationResult(success=True, message="User added to admin group."))
        except User.DoesNotExist:
            return MakeAdmin(operation_result=OperationResult(success=False, message="User not found."))


class RemoveAdmin(graphene.Mutation):
    """
    Removes the specified user from being an admin.
    """
    class Arguments:
        user_id = graphene.Int(required=True)

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_staff = False
            user.is_superuser = False
            user.groups.clear()
            user.groups.add(Group.objects.get(name='user'))
            user.save()      
            return RemoveAdmin(operation_result=OperationResult(success=True, message="User removed from admin group."))
        except User.DoesNotExist:
            return RemoveAdmin(operation_result=OperationResult(success=False, message="User not found."))
class UserMutations(graphene.ObjectType):
    register_user = RegisterUser.Field(description="Registers a new user with the specified username, password, and email.")
    make_admin = MakeAdmin.Field(description="Makes a user an admin.")
    remove_admin = RemoveAdmin.Field(description="Removes a user from being an admin.")