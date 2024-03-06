import graphene
from graphene_django import DjangoObjectType
from .models import Product

class ProductType(DjangoObjectType):
    """
    Represents the Product model in GraphQL. This type exposes all fields of the Product model,
    facilitating queries on products in the database.
    """
    class Meta:
        model = Product
        fields = '__all__'

class ProductsPerMonthType(graphene.ObjectType):
    """
    Represents the count of products created each month. It encapsulates
    the month and the count of products for easier aggregation and presentation.
    """
    month = graphene.String(description="The name of the month in 'Month YYYY' format.")
    product_count = graphene.Int(description="The count of products created in that month.")