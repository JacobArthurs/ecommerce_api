import graphene
from gql.types import OperationResult
from .models import Product
from graphql_jwt.decorators import user_passes_test

class CreateProduct(graphene.Mutation):
    """
    Creates a product based on the provided inputs. Validates input to ensure any provided cost or
    supply values are positive if provided.
    """
    class Arguments:
        name = graphene.String(required=True, description="The name of the product.")
        description = graphene.String(required=True, description="A detailed description of the product.")
        cost = graphene.Float(required=True, description="The cost of the product. Must be a positive value.")
        supply = graphene.Int(required=True, description="The available supply quantity of the product. Must be a positive number.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, name, description, cost, supply):
        if cost < 0:
            return CreateProduct(operation_result=OperationResult(success=False, message="Cost must be a positive value."))
        if supply < 0:
            return CreateProduct(operation_result=OperationResult(success=False, message="Supply must be a positive value."))
        if not name:
            return CreateProduct(operation_result=OperationResult(success=False, message="Name cannot be empty."))
        if not description:
            return CreateProduct(operation_result=OperationResult(success=False, message="Description cannot be empty."))

        product = Product(name=name, description=description, cost=cost, supply=supply)
        product.save()

        return CreateProduct(operation_result=OperationResult(success=True, message="Product created successfully."))

class UpdateProduct(graphene.Mutation):
    """
    Updates an existing product's details based on the provided inputs. Only non-null fields
    will be updated. Validates input to ensure any provided cost or supply values are positive.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the product to update, required.")
        name = graphene.String(description="The new name of the product, optional.")
        description = graphene.String(description="The new description of the product, optional.")
        cost = graphene.Float(description="The new cost of the product, must be positive if provided, optional.")
        supply = graphene.Int(description="The new supply quantity of the product, must be positive if provided, optional.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, id, **kwargs):
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return UpdateProduct(operation_result=OperationResult(success=False, message="Product not found."))
        
        for field, value in kwargs.items():
            if value is not None:
                if field == 'cost' and value < 0:
                    return UpdateProduct(operation_result=OperationResult(success=False, message="Cost must be a positive value."))
                if field == 'supply' and value < 0:
                    return UpdateProduct(operation_result=OperationResult(success=False, message="Supply must be a positive value."))
                if field == 'name' and not value:
                    return UpdateProduct(operation_result=OperationResult(success=False, message="Name cannot be empty."))
                if field == 'description' and not value:
                    return UpdateProduct(operation_result=OperationResult(success=False, message="Description cannot be empty."))
                setattr(product, field, value)
        
        product.save()
        
        return UpdateProduct(operation_result=OperationResult(success=True, message="Product updated successfully."))

class DeleteProduct(graphene.Mutation):
    """
    Deletes a product by its ID. If the product does not exist,
    the operation will still succeed but will indicate that no deletion was performed.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The unique ID of the product to be deleted.")

    operation_result = graphene.Field(OperationResult)

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    @staticmethod
    def mutate(root, info, id):
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return UpdateProduct(operation_result=OperationResult(success=False, message="Product not found."))
        
        product.delete()

        return DeleteProduct(operation_result=OperationResult(success=True, message="Product deleted successfully."))

class ProductMutations(graphene.ObjectType):
    create_product = CreateProduct.Field(description="Creates a new product with the specified details.")
    update_product = UpdateProduct.Field(description="Updates an existing product with new values for any of the specified fields.")
    delete_product = DeleteProduct.Field(description="Deletes the product identified by the given ID. Returns success=True if deleted.")