import graphene
from gql.types import OperationResult
from .models import Tag
from products.models import Product
from graphql_jwt.decorators import user_passes_test

class CreateTag(graphene.Mutation):
    """
    Creates a tag for a product based on the provided inputs. Validates input to ensure the 
    rating is valid if provided.
    """
    class Arguments:
        name = graphene.String(required=True, description="The name of the tag.")
        description = graphene.String(required=True, description="The description text of the tag.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, name, description):
        tag = Tag(name=name, description=description)
        tag.save()

        return CreateTag(operation_result=OperationResult(success=True, message="Tag created successfully."))

class UpdateTag(graphene.Mutation):
    """
    Updates an existing tag's details based on the provided inputs. Only non-null fields
    will be updated.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the tag to update.")
        name = graphene.String(required=True, description="The new name of the tag, optional.")
        description = graphene.String(required=True, description="The description text of the tag, optional.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, id, **kwargs):
        try:
            tag = Tag.objects.get(pk=id)
        except Tag.DoesNotExist:
            return UpdateTag(operation_result=OperationResult(success=False, message="Tag not found."))

        for field, value in kwargs.items():
            setattr(tag, field, value)

        tag.save()
        return UpdateTag(operation_result=OperationResult(success=True, message="Tag updated successfully."))

class DeleteTag(graphene.Mutation):
    """
    Deletes a tag by its ID.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The unique ID of the tag to be deleted.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, id):
        try:
            tag = Tag.objects.get(pk=id)
        except Tag.DoesNotExist:
            return DeleteTag(operation_result=OperationResult(success=False, message="Tag not found."))
        
        tag.delete()
        return DeleteTag(operation_result=OperationResult(success=True, message="Tag deleted successfully."))

class AddTagToProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True, description="The ID of the product to add a tag to.")
        tag_id = graphene.ID(required=True, description="The ID of the tag to add to the product.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, product_id, tag_id):
        """
        Adds a tag to a product.
        """
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return AddTagToProduct(operation_result=OperationResult(success=False, message="Product not found."))

        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return AddTagToProduct(operation_result=OperationResult(success=False, message="Tag not found."))

        # Add the tag to the product
        product.tags.add(tag)
        
        return AddTagToProduct(operation_result=OperationResult(success=True, message="Tag added to product successfully."))

class TagMutations(graphene.ObjectType):
    create_tag = CreateTag.Field(description="Creates a new tag with the specified details.")
    update_tag = UpdateTag.Field(description="Updates an existing tag with new values for any of the specified fields.")
    delete_tag = DeleteTag.Field(description="Deletes the tag identified by the given ID.")
    add_tag_to_product = AddTagToProduct.Field(description="Adds a tag to a product.")