import graphene
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import datetime, time
from .types import ProductType, ProductsPerMonthType
from .models import Product
from graphql_jwt.decorators import user_passes_test
from django.utils import timezone

class ProductQuery(graphene.ObjectType):
    all_products = graphene.List(
        ProductType, 
        description="Retrieve all products."
    )
    product_by_id = graphene.Field(
        ProductType, 
        id=graphene.Int(required=True, description="The ID of the product to retrieve."), 
        description="Retrieve a single product by its ID."
    )
    search_products = graphene.List(
        ProductType,
        name=graphene.String(default_value=None, description="A substring of the product name to filter by. Case-insensitive."),
        product_description=graphene.String(default_value=None, description="A substring of the product description to filter by. Case-insensitive."),
        min_cost=graphene.Float(default_value=None, description="The minimum cost of products to retrieve."),
        max_cost=graphene.Float(default_value=None, description="The maximum cost of products to retrieve."),
        min_supply=graphene.Int(default_value=None, description="The minimum supply of products to retrieve."),
        max_supply=graphene.Int(default_value=None, description="The maximum supply of products to retrieve."),
        start_date=graphene.Date(default_value=None, description="The start date of products to retrieve."),
        end_date=graphene.Date(default_value=None, description="The end date of products to retrieve."),
        tags=graphene.List(graphene.Int, default_value=None, description="The IDs of the tags to filter by."),
        description="Search for products based on various criteria such as name, description, cost range, and supply range."
    )
    products_per_month = graphene.List(
        ProductsPerMonthType, 
        last_n_months=graphene.Int(required=True, description="The number of months to include in the count, counting backwards from the current month."),
    )

    def resolve_all_products(self, info):
        """
        Fetches all product instances from the database.
        
        Returns:
            List of all Product instances.
        """
        return Product.objects.all()
    
    def resolve_product_by_id(self, info, id):
        """
        Retrieves a single Product by its ID.

        Returns:
            A Product if found, None otherwise.
        """
        return Product.objects.filter(pk=id).first()

    def resolve_search_products(self, info, **kwargs):
        """
        Searches for products matching the given criteria.
        
        Returns:
            List of Product instances matching the search criteria.
        """
        queryset = Product.objects.all()

        if kwargs.get('name'):
            queryset = queryset.filter(name__icontains=kwargs['name'])
        if kwargs.get('product_description'):
            queryset = queryset.filter(description__icontains=kwargs['product_description'])
        if kwargs.get('min_cost') is not None:
            queryset = queryset.filter(cost__gte=kwargs['min_cost'])
        if kwargs.get('max_cost') is not None:
            queryset = queryset.filter(cost__lte=kwargs['max_cost'])
        if kwargs.get('min_supply') is not None:
            queryset = queryset.filter(supply__gte=kwargs['min_supply'])
        if kwargs.get('max_supply') is not None:
            queryset = queryset.filter(supply__lte=kwargs['max_supply'])
        if kwargs.get('start_date') is not None:
            start_datetime = timezone.make_aware(datetime.combine(kwargs['start_date'], time.min), timezone.get_default_timezone())
            queryset = queryset.filter(created_at__gte=start_datetime)
        if kwargs.get('end_date') is not None:
            end_datetime = timezone.make_aware(datetime.combine(kwargs['end_date'], time.max), timezone.get_default_timezone())
            queryset = queryset.filter(created_at__lte=end_datetime)
        if kwargs.get('tags') is not None:
            queryset = queryset.filter(tags__id__in=kwargs['tags'])

        return queryset
    
    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    def resolve_products_per_month(self, info, last_n_months):
        """
        Calculates the number of products created each month for the last N months.
        
        Returns:
            A list of ProductsPerMonthType instances, each representing the product count for a month.
        """
        end_date = now().date().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
        start_date = end_date.replace(day=1) - relativedelta(months=last_n_months-1)

        queryset = Product.objects \
            .filter(created_at__date__gte=start_date, created_at__date__lte=end_date) \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(product_count=Count('id')) \
            .order_by('month')
        
        product_count_dict = {item['month'].strftime("%B %Y"): item['product_count'] for item in queryset}
        months_in_range = [(start_date + relativedelta(months=i)).strftime("%B %Y") for i in range(last_n_months)]

        return [ProductsPerMonthType(month=month, product_count=product_count_dict.get(month, 0)) for month in months_in_range]
