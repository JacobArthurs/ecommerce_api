import graphene
from datetime import datetime, time
from .types import ReviewType
from .models import Review

class ReviewQuery(graphene.ObjectType):
    all_reviews = graphene.List(
        ReviewType, 
        description="Retrieve all reviews."
    )
    review_by_id = graphene.Field(
        ReviewType, 
        id=graphene.Int(required=True, description="The ID of the review to retrieve."), 
        description="Retrieve a single review by its ID."
    )
    search_reviews = graphene.List(
        ReviewType,
        product_id=graphene.Int(required=True, description="The ID of the product to filter by."),
        title=graphene.String(default_value=None, description="A substring of the review title to filter by. Case-insensitive."),
        body=graphene.String(default_value=None, description="A substring of the review body to filter by. Case-insensitive."),
        min_rating=graphene.Float(default_value=None, description="The minimum rating of reviews to retrieve."),
        max_rating=graphene.Float(default_value=None, description="The maximum rating of reviews to retrieve."),
        start_date=graphene.Date(default_value=None, description="The start date of reviews to retrieve."),
        end_date=graphene.Date(default_value=None, description="The end date of reviews to retrieve."),
        description="Search for reviews based on various criteria such as title, body, rating range, and date range."
    )

    def resolve_all_reviews(self, info):
        """
        Fetches all reviews from the database.
        
        Returns:
            List of all reviews.
        """
        return Review.objects.all()
    
    def review_by_id(self, info, id):
        """
        Retrieves a single review by its ID.

        Returns:
            A review if found, None otherwise.
        """
        return Review.objects.filter(pk=id).first()

    def resolve_search_reviews(self, info, **kwargs):
        """
        Searches for reviews matching the given criteria.
        
        Returns:
            List of review instances matching the search criteria.
        """
        queryset = Review.objects.filter(product_id=kwargs['product_id'])

        if kwargs.get('title'):
            queryset = queryset.filter(name__icontains=kwargs['title'])
        if kwargs.get('body'):
            queryset = queryset.filter(description__icontains=kwargs['body'])
        if kwargs.get('min_rating') is not None:
            queryset = queryset.filter(cost__gte=kwargs['min_rating'])
        if kwargs.get('max_rating') is not None:
            queryset = queryset.filter(cost__lte=kwargs['max_rating'])
        if kwargs.get('start_date') is not None:
            start_datetime = datetime.combine(kwargs['start_date'], time.min)
            queryset = queryset.filter(created_at__gte=start_datetime)
        if kwargs.get('end_date') is not None:
            end_datetime = datetime.combine(kwargs['end_date'], time.max)
            queryset = queryset.filter(created_at__lte=end_datetime)
        
        return queryset