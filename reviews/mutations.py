import graphene
from gql.types import OperationResult
from .models import Review
from products.models import Product
from graphql_jwt.decorators import login_required

class CreateReview(graphene.Mutation):
    """
    Creates a review for a product based on the provided inputs. Validates input to ensure the 
    rating is valid if provided.
    """
    class Arguments:
        title = graphene.String(required=True, description="The title of the review.")
        body = graphene.String(required=True, description="The body text of the review.")
        rating = graphene.Int(required=True, description="The rating given in the review. Must be an integer.")
        product_id = graphene.ID(required=True, description="The ID of the product this review is for.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, title, body, rating, product_id):
        if rating < 1 or rating > 10:
            return CreateReview(operation_result=OperationResult(success=False, message="Rating must be between 1 and 10."))
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return CreateReview(operation_result=OperationResult(success=False, message="Product not found."))

        review = Review(title=title, body=body, rating=rating, product=product)
        review.save()

        return CreateReview(operation_result=OperationResult(success=True, message="Review created successfully."))

class UpdateReview(graphene.Mutation):
    """
    Updates an existing review's details based on the provided inputs. Only non-null fields
    will be updated. Validates input to ensure the rating is valid if provided.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the review to update.")
        title = graphene.String(description="The new title of the review, optional.")
        body = graphene.String(description="The new body text of the review, optional.")
        rating = graphene.Int(description="The new rating of the review. Must be an integer, optional.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, id, **kwargs):
        try:
            review = Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return UpdateReview(operation_result=OperationResult(success=False, message="Review not found."))

        for field, value in kwargs.items():
            if field == 'rating' and (value < 1 or value > 10):
                return UpdateReview(operation_result=OperationResult(success=False, message="Rating must be between 1 and 10."))
            setattr(review, field, value)

        review.save()
        return UpdateReview(operation_result=OperationResult(success=True, message="Review updated successfully."))

class DeleteReview(graphene.Mutation):
    """
    Deletes a review by its ID.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The unique ID of the review to be deleted.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, id):
        try:
            review = Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return DeleteReview(operation_result=OperationResult(success=False, message="Review not found."))
        
        review.delete()
        return DeleteReview(operation_result=OperationResult(success=True, message="Review deleted successfully."))

class ReviewMutations(graphene.ObjectType):
    create_review = CreateReview.Field(description="Creates a new review with the specified details.")
    update_review = UpdateReview.Field(description="Updates an existing review with new values for any of the specified fields.")
    delete_review = DeleteReview.Field(description="Deletes the review identified by the given ID.")